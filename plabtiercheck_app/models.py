from django.db import models
from django.contrib.auth.models import User

class Team(models.Model):
    name = models.CharField(max_length=100)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teams')

    def __str__(self):
        return self.name

class TeamMember(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='team_member')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members')
    is_approved = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.team.name}"