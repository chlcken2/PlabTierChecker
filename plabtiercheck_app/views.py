import logging

from allauth.socialaccount.providers.kakao.provider import KakaoProvider
from allauth.socialaccount.providers.oauth2.views import OAuth2Adapter, OAuth2LoginView, OAuth2CallbackView
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
import requests

# Create your views here.
from plabtiercheck_app.models import Player, PostGameStatistics, StandardDataSource
from plabtiercheck_app.utils.calculator import calculate_post_game_statistics


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
        'top_players': top_players  # 결과값을 템플릿으로 전달
    })


@login_required  # 로그인된 사용자만 이용 가능
def create_game(request):
    if request.method == 'POST':
        # 게임 정보 추출
        game_name = request.POST.get('game_name')
        game_type = request.POST.get('game_type')
        is_manager = request.POST.get('is_manager') == '1'
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')



        # 현재 로그인한 사용자를 가져와서 게임에 추가
        playertest = Player.objects.get(user=request.user)
        # player = request.user.player  # 현재 로그인한 사용자의 플레이어 정보 가져오기
        logging.debug("@playertest정보 : %s", playertest)  # player 객체 출력
        # logging.debug("@player정보 : %s", player)  # player 객체 출력

        # 게임 생성 및 저장
        game = StandardDataSource.objects.create(
            game_type=game_type,
            game_name=game_name,
            latitude=latitude,
            longitude=longitude,
            is_made=playertest
        )

        game.players.add(playertest)  # 게임에 플레이어 추가

        # 매니저인 경우 게임에 매니저 정보 추가
        if is_manager:
            game.manager = request.user
            game.is_manager = True
            game.save()

        # JSON 응답
        response_data = {
            'success': True,
            'message': '게임이 생성되었습니다.',
            'game_data': {
                'id': game.id,
                'game_name': game.game_name,
                'game_type': game.game_type,
                'latitude': game.latitude,
                'longitude': game.longitude,
                'is_manager': game.is_manager,
                'creator': game.manager.user.username if game.is_manager else player.user.username,
            }
        }
        return JsonResponse(response_data)

    return render(request, 'mypage.html')


@login_required
def mypage(request):
    user = request.user
    return render(request, 'mypage.html', {'user': user})


def player_detail(request):
    return render(request, 'player_detail.html')
