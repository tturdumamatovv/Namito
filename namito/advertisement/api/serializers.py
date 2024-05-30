from rest_framework import serializers
from namito.advertisement.models import Advertisement, Notification


class AdvertisementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertisement
        fields = ["image", 'title', 'description', 'button_link', 'button', 'page']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['title', 'description', 'date', 'image']

