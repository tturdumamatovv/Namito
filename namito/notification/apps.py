from django.apps import AppConfig


class NotificationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'namito.notification'

    def ready(self):
        import namito.notification.signals
