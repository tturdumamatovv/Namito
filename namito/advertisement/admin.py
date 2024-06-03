from django.contrib import admin

from namito.advertisement.models import Advertisement, Notification


class AdvertisementInline(admin.StackedInline):
    model = Advertisement
    extra = 0


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'date', 'image')
