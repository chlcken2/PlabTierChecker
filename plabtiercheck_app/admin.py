from django.contrib import admin

# Register your models here.
from plabtiercheck_app.models import Player, DefaultData, PerformanceData, LocationData

admin.site.register(Player)
admin.site.register(DefaultData)
admin.site.register(PerformanceData)
admin.site.register(LocationData)
