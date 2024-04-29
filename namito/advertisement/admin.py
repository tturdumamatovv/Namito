from django.contrib import admin

# Register your models here.
from namito.advertisement.models import Advertisement


class AdvertisementInline(admin.TabularInline):
    model = Advertisement
    extra = 0

