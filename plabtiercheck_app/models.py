from time import localtime, timezone

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import User


class PLAYER_TIER_TYPE(models.TextChoices):  # divmod 연산자로 3을 나눈후 몫과 나머지로 계산
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
    user = models.OneToOneField(User, related_name="player", on_delete=models.CASCADE)
    point = models.IntegerField(help_text="포인트", default=0)
    player_path = models.SlugField(max_length=20)
    one_day_game_participation = models.IntegerField(help_text="하루 참여 게임수", default=0)
    player_tier = models.CharField(
        max_length=2,
        choices=PLAYER_TIER_TYPE.choices,
        default=PLAYER_TIER_TYPE.ROOKIE,
    )
    now_latitude = models.FloatField(null=True, blank=True)
    now_longitude = models.FloatField(null=True, blank=True)
    one_intro = models.TextField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username + " #" + str(self.user.id)


class Manager(models.Model):
    user = models.OneToOneField(User, related_name="managers", on_delete=models.CASCADE)
    one_day_game_participation = models.IntegerField(help_text="하루 참여 게임수", default=0)
    created_at = models.DateTimeField(auto_now_add=True)


# player:1 = defaults:N
class StandardDataSource(models.Model):
    is_made = models.ForeignKey(Player, related_name="created_player", on_delete=models.CASCADE)
    players = models.ManyToManyField(Player, related_name="participate_players")
    manager = models.ForeignKey(User, related_name="managed_player", on_delete=models.SET_NULL, null=True)
    game_name = models.CharField(max_length=30, help_text="게임 이름")

    GAME_TYPES = (
        ('SO', '축구'),
        ('FU', '풋살')
    )
    game_type = models.CharField(
        max_length=2,
        choices=GAME_TYPES,
        default='FU'
    )
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    one_day_play_time = models.IntegerField(help_text="하루 평균 플레이 시간 (분)", default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Game ID: {self.id}, Created By: {self.is_made.user.username}"


# GPS 테이블 실시간 데이터 연동 / 반영?? (gps 연결, 연결 종료, 연결 지속 시간, 이동거리, 속도, 경기장)
class GPSDataSource(models.Model):
    player = models.ForeignKey(Player, related_name='gps_data_sources', on_delete=models.CASCADE)
    related_game = models.ForeignKey(StandardDataSource, related_name='gps_data_sources', on_delete=models.SET_NULL,
                                     null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, help_text="위도")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, help_text="경도")
    x_speed = models.FloatField(help_text="x축 속도", default=0)
    y_speed = models.FloatField(help_text="y축 속도", default=0)
    is_state = models.BooleanField(help_text="gps 연결 상태", default=True)
    connected_at = models.DateTimeField(auto_now_add=True, help_text="gps 연결 시간")
    dis_connected_at = models.DateTimeField(null=True, blank=True, help_text="GPS 연결 종료 시간")
    connecting_at = models.DurationField(help_text="GPS 연결 지속 시간")

    def __str__(self):
        return f"{self.player.user.username} - GPS Data {str(self.id)}"


# 같이 뛴 플레이어들에 대한 평가
# evaluator가 evaluatee를 평가한 점수와 피드백, evaluatee도 evaluator를 평가해야지만 데이터 반영
class TeammateEvaluationSource(models.Model):
    evaluator = models.ForeignKey(Player, related_name='evaluations_given', on_delete=models.CASCADE)
    evaluatee = models.ForeignKey(Player, related_name='evaluations_received', on_delete=models.CASCADE)
    score1 = models.BooleanField(help_text="POM 투표")
    score2 = models.IntegerField(help_text="기술적 능력", validators=[MinValueValidator(0), MaxValueValidator(10)],
                                 default=0)
    score3 = models.IntegerField(help_text="전술 이해도/수행력", validators=[MinValueValidator(0), MaxValueValidator(10)],
                                 default=0)
    score5 = models.IntegerField(help_text="팀워크", validators=[MinValueValidator(0), MaxValueValidator(10)], default=0)
    score6 = models.IntegerField(help_text="체력", validators=[MinValueValidator(0), MaxValueValidator(10)], default=0)
    score7 = models.IntegerField(help_text="경기 영향력", validators=[MinValueValidator(0), MaxValueValidator(10)],
                                 default=0)
    related_game = models.ForeignKey(StandardDataSource, related_name='teammate_evaluations', on_delete=models.SET_NULL,
                                     null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.evaluator.user.username} -> {self.evaluatee.user.username}"


# 매니저or심판이 존재할 경우 평가
class ManagerEvaluationSource(models.Model):
    evaluator = models.ForeignKey(Player, related_name='manager_evaluations', on_delete=models.CASCADE,
                                  help_text="매니저/심판")
    evaluatee = models.ForeignKey(Player, related_name='evaluations_by_manager', on_delete=models.CASCADE,
                                  help_text="평가 대상 플레이어")
    evaluation_declined = models.BooleanField(default=False, help_text="평가 거부 여부")
    score1 = models.BooleanField(help_text="POM 투표")
    score2 = models.IntegerField(help_text="기술적 능력", validators=[MinValueValidator(0), MaxValueValidator(10)],
                                 default=0)
    score3 = models.IntegerField(help_text="전술 이해도/수행력", validators=[MinValueValidator(0), MaxValueValidator(10)],
                                 default=0)
    score5 = models.IntegerField(help_text="팀워크", validators=[MinValueValidator(0), MaxValueValidator(10)], default=0)
    score6 = models.IntegerField(help_text="체력", validators=[MinValueValidator(0), MaxValueValidator(10)], default=0)
    score7 = models.IntegerField(help_text="경기 영향력", validators=[MinValueValidator(0), MaxValueValidator(10)],
                                 default=0)
    related_game = models.ForeignKey(StandardDataSource, related_name='manager_evaluations',
                                     on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.evaluator.user.username} 매니저 평가 -> {self.evaluatee.user.username}"


# 경기가 끝난 후 플레이어들의 통계
# 이동거리, 평균속도, 최고속도 '순위' 로직으로 구현
class PostGameStatistics(models.Model):
    player = models.ForeignKey(Player, related_name='post_game_statistics', on_delete=models.CASCADE)
    # plab_king_score = models.FloatField(help_text="종합 평균 점수", default=0.0)
    average_teammate_score = models.FloatField(help_text="팀원 평가 평균 점수", default=0.0)
    teammate_score_count = models.IntegerField(help_text="팀원 평가 투표 수", default=0)
    manager_referee_score = models.FloatField(help_text="매니저/심판 평가 점수", default=0.0)
    gps_statistics = models.JSONField(help_text="GPS 데이터 기반 통계", null=True, blank=True)
    performance_statistics = models.JSONField(help_text="성능 데이터 기반 통계", null=True, blank=True)
    distance_covered = models.FloatField(help_text="총 이동 거리 (m)")
    play_location = models.CharField(max_length=100, help_text="경기장", default='')
    average_speed = models.FloatField(help_text="평균 속도 (km/h)")
    top_speed = models.FloatField(help_text="최고 속도 (km/h)")
    modified_at = models.DateTimeField(auto_now=True)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Calculated Statistics for {self.player.user.username}"


# 하루 기준 모든 플레이어들의 통계 값
class TotalPlayerStatistics(models.Model):
    # plab_king_score = models.FloatField(help_text="종합 평균 점수", default=0.0)
    average_teammate_score = models.FloatField(help_text="팀원 평가 평균 점수", default=0.0)
    teammate_score_count = models.IntegerField(help_text="팀원 평가 투표 수", default=0)
    manager_referee_score = models.FloatField(help_text="매니저/심판 평가 점수", default=0.0)
    gps_statistics = models.JSONField(help_text="GPS 데이터 기반 통계", null=True, blank=True)
    performance_statistics = models.JSONField(help_text="성능 데이터 기반 통계", null=True, blank=True)
    distance_covered = models.FloatField(help_text="총 이동 거리 (m)")
    average_speed = models.FloatField(help_text="평균 속도 (km/h)")
    top_speed = models.FloatField(help_text="최고 속도 (km/h)")
    modified_at = models.DateTimeField(auto_now=True)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Total Player Statistics as of {self.modified_at.strftime('%Y-%m-%d')}"

# 데이터 분석 비교
