from django.apps import AppConfig


class CarappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'carapp'

    def ready(self):
        # Import signals to ensure they are registered
        from . import signals  # noqa: F401
