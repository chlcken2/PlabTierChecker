from datetime import datetime
from html import escape

from allauth.socialaccount.providers.kakao.provider import KakaoProvider
from allauth.socialaccount.providers.oauth2.views import OAuth2Adapter, OAuth2LoginView, OAuth2CallbackView
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
import requests
from plabtiercheck_app.models import Player, PostGameStatistics, StandardDataSource
from plabtiercheck_app.utils.calculator import calculate_area
from plabtiercheck_app.utils.convertor import get_game_type_display


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


def index(request):
    game_id = 1
    recent_players = Player.objects.all().order_by('-created_at')[:10]
    # calculated_score_by_manager = calculate_post_game_statistics(game_id)
    top_players = PostGameStatistics.objects.all().order_by('-average_teammate_score')[:10]
    return render(request, 'index.html', {
        'recent_players': recent_players,
        'top_players': top_players
    })


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

        if game_area['lat_lower'] <= player_lat <= game_area['lat_upper'] and game_area['lon_lower'] <= player_lon <= game_area['lon_upper']:
            games_data.append({
                'id': game.id,
                'creator': game.is_made.user.username,
                'game_name': game.game_name,
                'game_type': get_game_type_display(game.game_type),
                'match_time': game.created_at.strftime('%Y-%m-%dT%H:%M:%S'), # ISO 8601 형식
                'now_join_player': game.players.count(),
            })
    print('games_data', games_data)
    # 해당 게임정보 리턴
    return JsonResponse({'games': games_data})



@login_required
def mypage(request):
    user = request.user
    return render(request, 'mypage.html', {'user': user})


def player_detail(request):
    return render(request, 'player_detail.html')
