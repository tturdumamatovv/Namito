from django.contrib import admin

from namito.advertisement.models import Advertisement


class AdvertisementInline(admin.TabularInline):
    model = Advertisement
    extra = 0

