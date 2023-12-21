from allauth.socialaccount.providers.kakao.provider import KakaoProvider
from allauth.socialaccount.providers.oauth2.views import OAuth2Adapter, OAuth2LoginView, OAuth2CallbackView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import requests

# Create your views here.
from plabtiercheck_app.models import Player, PostGameStatistics


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
    # 최근 등록된 플레이어
    recent_players = Player.objects.all().order_by('-created_at')[:10]

    # 우수 플레이어 (PostGameStatistics 모델을 기준으로)
    # 이 예시에서는 단순화를 위해 PostGameStatistics 모델의 average_teammate_score만 사용
    top_players = PostGameStatistics.objects.order_by('-average_teammate_score')[:10]

    return render(request, 'index.html', {
        'recent_players': recent_players,
        'top_players': top_players
    })


@login_required
def mypage(request):
    user = request.user
    return render(request, 'mypage.html', {'user': user})


def player_detail(request):
    return render(request, 'player_detail.html')