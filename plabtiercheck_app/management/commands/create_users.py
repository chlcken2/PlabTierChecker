from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from faker import Faker
from plabtiercheck_app.models import Player


class Command(BaseCommand):
    help = 'Create 30 users using seeder'

    def handle(self, *args, **options):
        fake = Faker()

        for _ in range(30):
            # 유저 생성
            username = fake.user_name()
            password = 'password'
            user = User.objects.create_user(username=username, password=password)

            # 자동 생성된 Player 및 Player_info 인스턴스 검색
            player = user.player
            player_info = player.player_info

            Player.player_path = fake.slug()  # 무작위 슬러그
            # Faker로부터 무작위 데이터로 Player_info 업데이트
            player_info.point = fake.random_int(min=0, max=1000)  # 0과 1000 사이의 무작위 점수
            player_info.is_celebrity = fake.boolean()  # 무작위 부울 값
            player_info.player_tier = fake.random_int(min=0, max=16)
            player_info.game_participate_count = fake.random_int(min=0, max=1000)
            player_info.all_play_time = fake.random_int(min=0, max=1000)
            # 업데이트된 Player_info 인스턴스 저장
            Player.save()
            player_info.save()

        self.stdout.write(self.style.SUCCESS('30명의 유저와 player 정보가 성공적으로 생성되었습니다'))
