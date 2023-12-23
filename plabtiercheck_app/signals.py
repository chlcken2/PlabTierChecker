from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Player, StandardDataSource, Manager


# User 모델의 저장 시그널을 처리합니다.
@receiver(post_save, sender=User)
def create_player(sender, instance, created, **kwargs):
    if created:
        Player.objects.create(user=instance)


# StandardDataSource 모델의 저장 시그널을 처리합니다.
@receiver(post_save, sender=StandardDataSource)
def add_player_to_game(sender, instance, created, **kwargs):
    if created:
        # StandardDataSource 모델을 생성한 player 정보 가져오기
        player = instance.is_made

        # 프론트에서 manager 값이 1로 넘어오면 해당 user가 manager가 됨
        if instance.manager:
            manager_user = instance.manager.user
        else:
            manager_user = None  # manager 값이 1이 아니면 manager는 null

        # players에 추가
        instance.players.add(player)

        # manager_user가 존재하면 manager에 추가, 아니면 null
        instance.manager = manager_user
        instance.save()
