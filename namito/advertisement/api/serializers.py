from rest_framework import serializers
from namito.advertisement.models import Advertisement


class AdvertisementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertisement
        fields = ["image", 'title', 'description', 'button_link', 'button', 'page']
