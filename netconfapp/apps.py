from django.apps import AppConfig


class NetconfappConfig(AppConfig):
    name = 'netconfapp'

    def ready(self):
        from .scheduler import start_scheduler
        start_scheduler()
