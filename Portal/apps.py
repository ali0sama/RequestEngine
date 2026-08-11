from django.apps import AppConfig


class PortalConfig(AppConfig):
    name = 'Portal'

    def ready(self):
        from django.contrib.auth.signals import user_login_failed

        from .signals import log_failed_login

        user_login_failed.connect(log_failed_login)
