from datetime import datetime
from html import escape
from allauth.socialaccount.providers.kakao.provider import KakaoProvider
from allauth.socialaccount.providers.oauth2.views import OAuth2Adapter, OAuth2LoginView, OAuth2CallbackView
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
import requests
from django.views.decorators.http import require_POST
from plabtiercheck_app.models import StandardDataSource, Player_info, Player
from plabtiercheck_app.utils.calculator import calculate_area
from plabtiercheck_app.utils.convertor import get_game_type_display, get_tier_display
from plabtiercheck_app.utils.getAllauthInfo import get_user_profile_image


class KakaoOAuth2Adapter(OAuth2Adapter):
    provider_id = KakaoProvider.id
    access_token_url = "https://kauth.kakao.com/oauth/token"
    authorize_url = "https://kauth.kakao.com/oauth/authorize"
    profile_url = "https://kapi.kakao.com/v2/user/me"

    def complete_login(self, request, app, token, **kwargs):
        headers = {"Authorization": "Bearer {0}".format(token.token)}

        resp = requests.get(self.profile_url, headers=headers)
        resp.raise_for_status()
        extra_data = resp.json()

        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(KakaoOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(KakaoOAuth2Adapter)


# StandardDataSource에 속한 players들은 게임에 참여한 회원이야 즉 count로 게임에 많이 참여한 회원 수를 추출하고
# TeammateEvaluationSource의 evaluator는 평가한 Player이니까 TeammateEvaluationSource를 평가한 Player의 count로 회원이 평가한 수를 뽑아서
# 서로 더한 다음 평균값이 높은 순서대로 10명을 뽑기
def index(request):
    # 1. 랭킹 우수 플레이어 // 우수 랭커 10명
    ranking_players = Player_info.objects.order_by('-point')[:10]
    ranking_player_tiers = [get_tier_display(player_info.player_tier) for player_info in ranking_players]

    ranking_players = list(zip(ranking_players, ranking_player_tiers))


    # # 2. 열정 플레이어 // 게임에 많이 참여하고 많은 평가를 해준 회원 /  -> 추후 게임시간으로 갱신
    passion_players = Player_info.objects.order_by('-game_participation_count')[:10]
    passion_player_tiers = [get_tier_display(player_info.player_tier) for player_info in passion_players]
    passion_players = list(zip(passion_players, passion_player_tiers))

    # 3.celebrity_players = 셀럽 플레이어 checked
    celebrity_players = Player_info.objects.filter(is_celebrity=True)[:10]
    celebrity_player_tiers = [get_tier_display(player_info.player_tier) for player_info in celebrity_players]
    celebrity_players = list(zip(celebrity_players, celebrity_player_tiers))

    context = {
        'ranking_players': ranking_players,
        'passion_players': passion_players,
        'celebrity_players': celebrity_players,
    }
    return render(request, 'index.html', context)


@login_required  # 로그인된 사용자만 이용 가능
def create_game(request):
    if request.method == 'POST':
        # 게임 정보 추출
        game_name = escape(request.POST.get('game_name'))
        game_type = escape(request.POST.get('game_type'))
        is_manager = True if escape(request.POST.get('is_manager')) == "true" else False
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        player = request.user.player
        # 게임 생성 및 저장

        game = StandardDataSource.objects.create(
            game_type=game_type,
            game_name=game_name,
            latitude=latitude,
            longitude=longitude,
            is_made=player
        )

        game.players.add(player)
        # 매니저인 경우 게임에 매니저 정보 추가
        if is_manager:
            game.manager = request.user
            game.save()

        # JSON 응답 결과, -> 응답 결과 분리 예정
        response_data = {
            'success': True,
            'message': '게임이 생성되었습니다.',
            'game_data': {
                'id': game.id,
                'game_name': game.game_name,
                'game_type': game.game_type,
                'latitude': game.latitude,
                'longitude': game.longitude,
                'creator': game.is_made.user.username,
            }
        }
        return JsonResponse(response_data)

    return render(request, 'mypage.html')


# 플레이어의 위도경도 시간과 StandardDataSource의 위도경도, 시간을 가져와서 조건에 부합한 게임 정보만 리턴
# 시간 조건 당일생성, 초과
@require_POST
@login_required
def get_game(request):
    #  당일 생성된 게임 필터링
    filtered_games = StandardDataSource.objects.filter(
        created_at__date=datetime.now().date(),
    )

    #  당일 생성된 게임 중 위도경도 필터링
    games_data = []
    for game in filtered_games:
        player_lat = float(request.POST.get('latitude'))
        player_lon = float(request.POST.get('longitude'))
        game_area = calculate_area(float(game.latitude), float(game.longitude))
        is_joined = True if request.user.player in game.players.all() else False

        if game_area['lat_lower'] <= player_lat <= game_area['lat_upper'] and game_area['lon_lower'] <= player_lon <= game_area['lon_upper']:
            games_data.append({
                'id': game.id,
                'is_joined': is_joined,
                'creator': game.is_made.user.username,
                'game_name': game.game_name,
                'game_type': get_game_type_display(game.game_type),
                'match_time': game.created_at.strftime('%Y-%m-%dT%H:%M:%S'), # ISO 8601 형식
                'now_join_player': game.players.count(),
            })
    print('games_data', games_data)
    # 해당 게임정보 리턴
    return JsonResponse({'games': games_data})


# 게임에 참가
# 조건: 본인 1번 이상 참여 불가, TODO 2시간 이내 게임 참여 불가
@require_POST
@login_required
def join_game(request):
    game_id = request.POST.get('game_id')
    user = request.user

    # 본인이 게임에 참여한 경우
    if user.player in StandardDataSource.objects.get(id=game_id).players.all():
        return JsonResponse({'status': 'error', 'message': '이미 해당 게임에 참여하셨습니다.'})

    StandardDataSource.objects.get(id=game_id).players.add(user.player)

    return JsonResponse({'status': 'success', 'message': '게임 참여 완료'})


@login_required
def mypage(request):
    user = request.user
    return render(request, 'mypage.html', {'user': user})


def player_detail(request, player_id):
    player = get_object_or_404(Player, pk=player_id)
    profile_image =get_user_profile_image(player.user)
    player_info = Player_info.objects.get(player=player)
    player_tier_en = player_info.player_tier
    player_tier_ko = get_tier_display(player_info.player_tier)

    context = {'player': player,
               'player_info': player_info,
               'player_tier_ko': player_tier_ko,
               'player_tier_en': player_tier_en,
               'profile_image': profile_image}

    return render(request, 'player_detail.html', context)


def faq(request):
    return render(request, 'faq.html')