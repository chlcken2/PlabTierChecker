from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Player, StandardDataSource


# User 모델의 저장 시그널을 처리합니다.
@receiver(post_save, sender=User)
def create_player(sender, instance, created, **kwargs):
    if created:
        # User가 생성된 경우 Player 모델에 연결된 플레이어 생성
        Player.objects.create(user=instance)


# StandardDataSource 모델의 저장 시그널을 처리합니다.
@receiver(post_save, sender=StandardDataSource)
def add_player_to_game(sender, instance, created, **kwargs):
    if created:
        # 게임이 생성된 경우, 생성자를 player로 추가하고 is_made에 등록
        instance.player.add(instance.manager.player)
        instance.is_made.add(instance.manager.player)
