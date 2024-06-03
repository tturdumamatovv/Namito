from django.apps import AppConfig
from django.db.models.signals import post_save
from django.dispatch import receiver



class AdvertisementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'namito.advertisement'

    def ready(self):
        # Перенесите импорты внутрь метода ready
        from .models import Notification
        from .firebase import send_firebase_notification
        from namito.users.models import User

        @receiver(post_save, sender=Notification)
        def send_notification_on_create(sender, instance, created, **kwargs):
            if created:
                users_with_tokens = User.objects.exclude(fcm_token__isnull=True).exclude(fcm_token__exact='')

                for user in users_with_tokens:
                    send_firebase_notification(user.fcm_token, instance.title, instance.description,
                                               instance.image.url if instance.image else None)
