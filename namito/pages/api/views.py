from rest_framework import generics
from rest_framework.response import Response

from namito.pages.api.serializers import MainPageSerializer, StaticPageSerializer
from namito.pages.models import MainPage, StaticPage
from namito.pages.api import pages_default_texts

class MainPageView(generics.ListAPIView):
    queryset = MainPage.objects.all()
    serializer_class = MainPageSerializer


class StaticPageDetailView(generics.RetrieveAPIView):
    queryset = StaticPage.objects.all()
    serializer_class = StaticPageSerializer
    lookup_field = 'slug'

    def get_object(self):
        slug = self.kwargs['slug']
        instance = None

        try:
            instance = StaticPage.objects.get(slug=slug)
        except StaticPage.DoesNotExist:
            if slug == 'about-us':
                instance = StaticPage.objects.create(
                    title=pages_default_texts.ABOUTUS_TITLE_EN,
                    title_ru=pages_default_texts.ABOUTUS_TITLE_RU,
                    title_en=pages_default_texts.ABOUTUS_TITLE_EN,

                    content=pages_default_texts.ABOUTUS_CONTENT_EN,
                    content_ru=pages_default_texts.ABOUTUS_CONTENT_RU,
                    content_en=pages_default_texts.ABOUTUS_CONTENT_EN,
                    slug="about-us"
                )
            elif slug == 'delivery':
                instance = StaticPage.objects.create(
                    title="Delivery",
                    content="Your delivery content here...",
                    slug="delivery"
                )

        return instance

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
