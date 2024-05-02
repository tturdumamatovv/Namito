from rest_framework import generics

from namito.advertisement.api.serializers import AdvertisementSerializer
from namito.pages.models import MainPage


class AdvertisementView(generics.ListAPIView):
    queryset = MainPage.objects.all()
    serializer_class = AdvertisementSerializer
