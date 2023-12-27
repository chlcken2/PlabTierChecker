from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from faker import Faker


class Command(BaseCommand):
    help = 'Create 30 users using seeder'

    def handle(self, *args, **options):
        fake = Faker()

        # 30명의 유저 생성
        for _ in range(30):
            username = fake.user_name()
            password = 'password'
            User.objects.create_user(username=username, password=password)

        self.stdout.write(self.style.SUCCESS('Successfully created 30 users'))
