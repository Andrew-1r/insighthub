from django.apps import AppConfig


class DashboardappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboardapp'

    def ready(self):
        import dashboardapp.signals
