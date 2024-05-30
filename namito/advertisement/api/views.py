from rest_framework import generics
import logging

from namito.advertisement.api.serializers import AdvertisementSerializer
from namito.pages.models import MainPage

from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from namito.advertisement.models import Notification
from .serializers import NotificationSerializer


class AdvertisementView(generics.ListAPIView):
    queryset = MainPage.objects.all()
    serializer_class = AdvertisementSerializer


logger = logging.getLogger(__name__)


from django.db.models.signals import post_save
from django.dispatch import receiver
from namito.advertisement.models import Notification


@receiver(post_save, sender=Notification)
def send_notification(sender, instance, **kwargs):
    logger.info("Notification created. Sending notification.")
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    import json

    # Получаем канал WebSocket
    channel_layer = get_channel_layer()

    # Отправляем уведомление по каналу WebSocket
    async_to_sync(channel_layer.group_send)(
        "notifications",  # Имя группы, в которую будет отправлено уведомление
        {
            "type": "send_notification",  # Тип сообщения для consumer'а
            "notification": {
                "id": instance.id,
                "title": instance.title,
                "description": instance.description,
                "date": instance.date.strftime("%Y-%m-%d %H:%M:%S"),
                "image": instance.image.url if instance.image else None,
            }
        }
    )
