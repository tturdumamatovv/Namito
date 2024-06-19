import logging

from django.contrib import admin
from django.contrib import messages

from namito.advertisement.models import Advertisement, Notification
from namito.advertisement.firebase import send_firebase_notification
from namito.users.models import User

logger = logging.getLogger(__name__)


class AdvertisementInline(admin.StackedInline):
    model = Advertisement
    extra = 0



@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'date', 'image')
    actions = ['send_notification']

    def send_notification(self, request, queryset):
        # Получаем всех пользователей, которые должны получить уведомление
        users_with_tokens = User.objects.filter(
            receive_notifications=True
        ).exclude(fcm_token__isnull=True).exclude(fcm_token__exact='')

        for notification in queryset:
            for user in users_with_tokens:
                try:
                    # Проверяем наличие токена перед отправкой уведомления
                    if user.fcm_token:
                        image_url = request.build_absolute_uri(notification.image.url) if notification.image else None
                        send_firebase_notification(
                            user.fcm_token,
                            notification.title,
                            notification.description,
                            notification.date,
                            image_url
                        )
                except Exception as e:
                    # Логируем ошибку, но не прерываем выполнение цикла
                    logger.error(f"Error sending notification to user {user.username}: {e}")
                    messages.error(request, f"Error sending notification to user {user.username}: {e}")

        self.message_user(request, "Notifications sent successfully")

    send_notification.short_description = "Отправить выбранные уведомления"
