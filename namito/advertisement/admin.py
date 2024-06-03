from django.contrib import admin

from namito.advertisement.models import Advertisement, Notification
from namito.advertisement.firebase import send_firebase_notification


class AdvertisementInline(admin.StackedInline):
    model = Advertisement
    extra = 0


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'date', 'image')
    actions = ['send_notification']

    def send_notification(self, request, queryset):
        for notification in queryset:
            image_url = notification.image.url if notification.image else None
            send_firebase_notification(notification.title, notification.description, image_url)
        self.message_user(request, "Notifications sent successfully")

    send_notification.short_description = "Отправить выбранные уведомления"
