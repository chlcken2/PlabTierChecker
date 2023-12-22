from django.apps import AppConfig


class PlabtiercheckAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'plabtiercheck_app'

    def ready(self):
        import plabtiercheck_app.signals