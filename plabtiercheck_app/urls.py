from django.urls import path, include
from plabtiercheck_app import views

urlpatterns = [
    path('', views.index),
    path('mypage/', views.mypage),
    path("<int:player_id>/", views.player_detail, name="player_detail"),
    # path('create_team/', views.create_team, name='create_team'),
    # path('team/<int:team_id>/', views.team_detail, name='team_detail'),
    # path('team/<int:team_id>/join/', views.join_team, name='join_team'),
    # path('member/<int:member_id>/accept/', views.accept_member, name='accept_member'),
]

