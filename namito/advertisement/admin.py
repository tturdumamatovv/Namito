from django.contrib import admin

from namito.advertisement.models import Advertisement, Notification
from namito.advertisement.firebase import send_firebase_notification
from namito.users.models import User


class AdvertisementInline(admin.StackedInline):
    model = Advertisement
    extra = 0


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'date', 'image')
    actions = ['send_notification']

    def send_notification(self, request, queryset):
        for notification in queryset:
            users_with_tokens = User.objects.exclude(fcm_token__isnull=True).exclude(fcm_token__exact='')

            for user in users_with_tokens:
                send_firebase_notification(user.fcm_token, notification.title, notification.description, notification.image.url if notification.image else None)

        self.message_user(request, "Notifications sent successfully")

    send_notification.short_description = "Отправить выбранные уведомления"
