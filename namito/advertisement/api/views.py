from rest_framework import generics

from namito.advertisement.api.serializers import AdvertisementSerializer, NotificationSerializer
from namito.pages.models import MainPage
from namito.advertisement.models import Notification


class AdvertisementView(generics.ListAPIView):
    queryset = MainPage.objects.all()
    serializer_class = AdvertisementSerializer


class NotificationList(generics.ListAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
