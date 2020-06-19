from django.apps import AppConfig


class CuKkInstrukcjeConfig(AppConfig):
    name = 'instructions'
    verbose_name = 'Instructions'

    def ready(self):
        from . import signals
