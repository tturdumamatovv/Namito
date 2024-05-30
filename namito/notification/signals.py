from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from namito.orders.models import Order


@receiver(post_save, sender=Order)
def notify_user_order_status(sender, instance, **kwargs):
    if instance.status == 1:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{instance.user.id}",
            {
                "type": "send_notification",
                "message": f"Your order #{instance.order_number} has been delivered."
            }
        )
