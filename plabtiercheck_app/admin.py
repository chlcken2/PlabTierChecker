from django.contrib import admin

# Register your models here.
from plabtiercheck_app.models import Player, StatisticData, PerformanceData

admin.site.register(Player)
admin.site.register(StatisticData)
admin.site.register(PerformanceData)
