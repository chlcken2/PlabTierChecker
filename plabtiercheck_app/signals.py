from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Player, StandardDataSource, Manager, Player_info


# User 모델의 저장 시그널을 처리합니다.
@receiver(post_save, sender=User)
def create_player(sender, instance, created, **kwargs):
    if created:
        Player.objects.create(user=instance)


@receiver(post_save, sender=Player)
def create_player_info(sender, instance, created, **kwargs):
    if created:
        Player_info.objects.create(player=instance)


@receiver(post_save, sender=User)
def create_manager(sender, instance, created, **kwargs):
    if created:
        Manager.objects.create(user=instance)


# StandardDataSource 모델의 저장 시그널을 처리합니다.
@receiver(post_save, sender=StandardDataSource)
def add_player_to_game(sender, instance, created, **kwargs):
    if created:
        # StandardDataSource 모델을 생성한 player 정보 가져오기
        player = instance.is_made

        # players에 추가
        instance.players.add(player)

        instance.save()
