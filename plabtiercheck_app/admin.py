from django.contrib import admin

# Register your models here.
from plabtiercheck_app.models import Player, StandardDataSource, GPSDataSource, TeammateEvaluationSource, \
    ManagerEvaluationSource, PostGameStatistics, TotalPlayerStatistics, Manager

admin.site.register(Player)
admin.site.register(StandardDataSource)
admin.site.register(GPSDataSource)
admin.site.register(TeammateEvaluationSource)
admin.site.register(ManagerEvaluationSource)
admin.site.register(PostGameStatistics)
admin.site.register(TotalPlayerStatistics)
admin.site.register(Manager)