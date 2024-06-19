from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .models import Order

from firebase_admin import messaging


@receiver(pre_save, sender=Order)
def track_status_change(sender, instance, **kwargs):
    if instance.pk:
        original_order = Order.objects.get(pk=instance.pk)
        instance._original_status = original_order.status


@receiver(post_save, sender=Order)
def send_order_status_notification(sender, instance, created, **kwargs):
    if created:
        instance._original_status = instance.status
    else:
        if instance.status != getattr(instance, '_original_status', None):
            instance._original_status = instance.status

    user = instance.user
    if user and user.fcm_token:
        try:
            if created:
                message_title = 'Ваш заказ оформлен'
            else:
                if instance.status == 1:
                    message_title = 'Заказ доставлен'
                elif instance.status == 2:
                    message_title = 'Заказ отменен'
                elif instance.status == 0:
                    message_title = 'Заказ в процессе'
                elif instance.status == 3:
                    message_title = 'Заказ отправлен'
                else:
                    message_title = 'Статус заказа изменен'

            message_body = (f'{instance.created_at.strftime("%d.%m.%Y")}, {instance.order_number}, '
                            f'{instance.get_status_display()}.')
            data = {
                "order_id": f"{instance.order_number}",
                "order_date": instance.created_at.strftime("%d.%m.%Y"),
                "order_status": instance.get_status_display(),
                "notification_type": "order"
            }
            message = messaging.Message(
                notification=messaging.Notification(title=message_title, body=message_body),
                data=data,
                token=user.fcm_token
            )
            response = messaging.send(message)
            print('Successfully sent message:', response)
        except Exception as e:
            print(f'Error sending message for order {instance.order_number}: {str(e)}')
    else:
        print(f'FCM token is not available for the user with order {instance.order_number}.')

