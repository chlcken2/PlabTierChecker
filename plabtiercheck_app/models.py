from time import localtime, timezone

from django.db import models
from django.contrib.auth.models import User


class PlayerTierType(models.TextChoices):  # 3 나눈후 몫과 나머지로 계산
    PRO1 = '1', '프로3'
    PRO2 = '2', '프로2'
    PRO3 = '3', '프로1'
    SEMIPRO1 = '4', '세미프로3'
    SEMIPRO2 = '5', '세미프로2'
    SEMIPRO3 = '6', '세미프로1'  # level 3
    AMATEUR1 = '7', '아마추어3'
    AMATEUR2 = '8', '아마추어2'
    AMATEUR3 = '9', '아마추어1'
    BEGINNER1 = '10', '비기너3'
    BEGINNER2 = '11', '비기너2'
    BEGINNER3 = '12', '비기너1'
    STARTER1 = '13', '스타터3'
    STARTER2 = '14', '스타터2'
    STARTER3 = '15', '스타터1'
    ROOKIE = '16', '루키'


class Player(models.Model):
    user = models.ForeignKey(User, related_name="players", on_delete=models.CASCADE)
    player_name = models.CharField(max_length=100)
    player_path = models.SlugField(max_length=20)
    player_tier = models.CharField(
        max_length=2,
        choices=PlayerTierType.choices,
        default=PlayerTierType.ROOKIE,
    )
    one_intro = models.TextField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.player_name + "+ #" + str(self.user.id)


# player:1 = defaults:N
class DefaultData(models.Model):
    player = models.ForeignKey(Player, related_name="defaults_data", on_delete=models.CASCADE)

    class GameType(models.TextChoices):
        SOCCER = 'SO', '축구'
        FUTSAL = 'FU', '풋살'

    game_type = models.CharField(
        max_length=2,
        choices=GameType.choices,
        default=GameType.FUTSAL,
    )
    one_day_game_participation = models.IntegerField(help_text="하루 참여 게임수", default=1)
    one_day_play_time = models.IntegerField(help_text="하루 평균 플레이 시간 (분)", default=0)
    played_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.player.player_name + "#" + str(self.player.user.id)


# 한 경기에 대한 데이터
# StatisticData:1 = PerformanceData:1
class PerformanceData(models.Model):
    default_data = models.OneToOneField(DefaultData, related_name='performances_data', on_delete=models.CASCADE)
    distance_covered = models.FloatField(help_text="총 이동 거리 (m)")
    play_location = models.CharField(max_length=100, help_text="경기장", default='')
    average_speed = models.FloatField(help_text="평균 속도 (km/h)")
    top_speed = models.FloatField(help_text="최고 속도 (km/h)")
    played_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.default_data.player.user.username + "#" + str(self.default_data.player.user.id)


# 해당 테이블 실시간 데이터 변동?? (gps 연결, 연결 종료, 연결 지속 시간, 이동거리, 속도, 경기장)
class LocationData(models.Model):
    default_data = models.OneToOneField(DefaultData, related_name='locations_data', on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, help_text="위도")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, help_text="경도")
    x_speed = models.FloatField(help_text="x축 속도", default=0)
    y_speed = models.FloatField(help_text="y축 속도", default=0)
    connected_at = models.DateTimeField(auto_now_add=True, help_text="gps 연결 시간")
    dis_connected_at = models.DateTimeField(null=True, blank=True, help_text="GPS 연결 종료 시간")  # 수정 필요
    connecting_at = models.DurationField(help_text="GPS 연결 지속 시간")  # 수정 필요

    def __str__(self):
        return self.default_data.player.user.username + "#" + str(self.default_data.player.user.id)

# 매니저
# 같이 뛴 플레이어
