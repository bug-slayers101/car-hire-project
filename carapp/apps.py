import sys
from django.apps import AppConfig


def patch_django_context_copy_for_python_314():
    """
    Django 4.2's BaseContext.__copy__ relies on behavior that changed in
    Python 3.14. Patch it at startup so admin templates can render safely.
    """
    if sys.version_info < (3, 14):
        return

    from django.template.context import BaseContext

    if getattr(BaseContext, "_python_314_copy_patch", False):
        return

    def _base_context_copy(self):
        duplicate = object.__new__(self.__class__)
        duplicate.__dict__ = self.__dict__.copy()
        duplicate.dicts = self.dicts[:]
        return duplicate

    BaseContext.__copy__ = _base_context_copy
    BaseContext._python_314_copy_patch = True


class CarappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'carapp'

    def ready(self):
        patch_django_context_copy_for_python_314()
        # Import signals to ensure they are registered
        from . import signals  # noqa: F401
