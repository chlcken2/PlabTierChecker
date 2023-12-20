from django.db import models
from django.contrib.auth.models import User


class Player(models.Model):
    user = models.ForeignKey(User, related_name="players", on_delete=models.CASCADE)
    player_name = models.CharField(max_length=100)
    player_path = models.CharField(max_length=20)

    class PlayerTier(models.TextChoices): # 3 나눈후 몫과 나머지로 계산
        PRO1 = '1', '프로1'
        PRO2 = '2', '프로2'
        PRO3 = '3', '프로3'
        SEMIPRO1 = '4', '세미프로1'
        SEMIPRO2 = '5', '세미프로2'
        SEMIPRO3 = '6', '세미프로3'
        AMATEUR1 = '7', '아마추어1'
        AMATEUR2 = '8', '아마추어2'
        AMATEUR3 = '9', '아마추어3'
        BEGINNER1 = '10', '비기너1'
        BEGINNER2 = '11', '비기너2'
        BEGINNER3 = '12', '비기너3'
        STARTER1 = '13', '스타터1'
        STARTER2 = '14', '스타터2'
        STARTER3 = '15', '스타터3'
        ROOKIE = '16', '루키'

    player_tier = models.CharField(
        max_length=2,
        choices=PlayerTier.choices,
        default=PlayerTier.ROOKIE,
    )

    one_intro = models.TextField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.player_name


class StatisticData(models.Model):
    player = models.ForeignKey(Player, related_name="statistics", on_delete=models.CASCADE)

    class GameType(models.TextChoices):
        SOCCER = 'SO', '축구'
        FUTSAL = 'FU', '풋살'
    game_type = models.CharField(
        max_length=2,
        choices=GameType.choices,
        default=GameType.FUTSAL,
    )
    game_count = models.IntegerField()
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.player.player_name + " " + "statistics"


class PerformanceData(models.Model):
    player = models.ForeignKey(Player, related_name='performances', on_delete=models.CASCADE)
    distance_covered = models.FloatField(help_text="총 이동 거리 (km)")
    average_speed = models.FloatField(help_text="평균 속도 (km/h)")
    top_speed = models.FloatField(help_text="최고 속도 (km/h)")
    game_participation = models.IntegerField(help_text="경기 참여 횟수")
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.player.player_name + " " + "performance"