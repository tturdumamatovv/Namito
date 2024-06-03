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

        @receiver(post_save, sender=Notification)
        def send_notification_on_create(sender, instance, created, **kwargs):
            if created:
                image_url = instance.image.url if instance.image else None
                send_firebase_notification(instance.title, instance.description, image_url)
