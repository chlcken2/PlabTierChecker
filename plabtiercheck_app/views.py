from allauth.socialaccount.providers.kakao.provider import KakaoProvider
from allauth.socialaccount.providers.oauth2.views import OAuth2Adapter, OAuth2LoginView, OAuth2CallbackView
from allauth.socialaccount.models import SocialApp
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import render, redirect
import requests

# Create your views here.
from plabtiercheck_app.models import Player, PostGameStatistics


def index(request):
    social_apps = SocialApp.objects.all()
    recent_players = Player.objects.all().order_by('-created_at')[:10]

    top_players = PostGameStatistics.objects.annotate(
        total_score=F('average_teammate_score') + F('manager_referee_score')
    ).order_by('-total_score')[:10]
    return render(request, 'index.html', {
        'recent_players': recent_players,
        'top_players': top_players
    })


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

def player_detail(request):
    return render(request, 'player_detail.html')

# @csrf_exempt  # AJAX 요청을 위한 CSRF 예외 처리
# @login_required
# def create_team(request):
#     if request.method == 'POST':
#         print("request.POST", request.POST)
#         team_name = request.POST.get('teamName')
#         team_path = request.POST.get('teamPath')
#         activity_days = request.POST.get('activity_days')
#         activity_time = request.POST.get('activity_time')
#         activity_location = request.POST.get('activity_location')
#         age_range = request.POST.get('age_range')
#
#         # 여기에 추가 필드 처리
#
#         # Team 객체 생성
#         team = Team.objects.create(
#             creator=request.user,
#             teamName=team_name,
#             teamPath=team_path,
#             activity_location=activity_location,
#             team_profile_image="none",
#             activity_days=activity_days,
#             activity_time=activity_time,
#             age_range=age_range
#             # 여기에 추가 필드 할당
#         )
#
#         return JsonResponse({"success": True, "message": "팀이 성공적으로 생성되었습니다."})
#
#     return JsonResponse({"success": False, "message": "잘못된 요청입니다."})

# @login_required
# def create_team(request):
#     if request.method == 'POST':
#         name = request.POST.get('name')
#         team = Team.objects.create(name=name, creator=request.user)
#         return redirect('team_detail', team_id=team.id)
#
#     return render(request, 'create_team.html')
#
# @login_required
# def join_team(request, team_id):
#     team = get_object_or_404(Team, id=team_id)
#     TeamMember.objects.create(user=request.user, team=team)
#     return redirect('team_detail', team_id=team.id)
#
# @login_required
# def accept_member(request, member_id):
#     member = get_object_or_404(TeamMember, id=member_id)
#     if request.user == member.team.creator:
#         member.is_approved = True
#         member.save()
#     return redirect('team_detail', team_id=member.team.id)
#
# def team_detail(request, team_id):
#     team = get_object_or_404(Team, id=team_id)
#     members = team.members.all()
#     return render(request, 'team_detail.html', {'team': team, 'members': members})
