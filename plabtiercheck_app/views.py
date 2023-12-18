from allauth.socialaccount.providers.kakao.provider import KakaoProvider
from allauth.socialaccount.providers.oauth2.views import OAuth2Adapter, OAuth2LoginView, OAuth2CallbackView
from allauth.socialaccount.models import SocialApp
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
import requests
from django.http import HttpResponse
import random
import json
from django.template import loader


# Create your views here.
from plabtiercheck_app.models import Team, TeamMember


def index(request):
    social_apps = SocialApp.objects.all()
    print(social_apps)
    return render(request, 'index.html')


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

@login_required
def mypage(request):
    user = request.user
    return render(request, 'mypage.html', {'user': user})

@login_required
def create_team(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        team = Team.objects.create(name=name, creator=request.user)
        return redirect('team_detail', team_id=team.id)

    return render(request, 'create_team.html')

@login_required
def join_team(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    TeamMember.objects.create(user=request.user, team=team)
    return redirect('team_detail', team_id=team.id)

@login_required
def accept_member(request, member_id):
    member = get_object_or_404(TeamMember, id=member_id)
    if request.user == member.team.creator:
        member.is_approved = True
        member.save()
    return redirect('team_detail', team_id=member.team.id)

def team_detail(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    members = team.members.all()
    return render(request, 'team_detail.html', {'team': team, 'members': members})