from django.apps import AppConfig


class EsgDataConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'esg_data'



    def ready(self):
        import esg_data.signals
