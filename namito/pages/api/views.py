from rest_framework import generics
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from namito.pages.api.serializers import MainPageSerializer, StaticPageSerializer
from namito.pages.models import MainPage, StaticPage


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
            # Если страница не существует, создаем новую
            if slug == 'about-us':
                instance = StaticPage.objects.create(
                    title="About Us",
                    content="Your about us content here...",
                    slug="about-us"
                )
            elif slug == 'delivery':
                instance = StaticPage.objects.create(
                    title="Delivery",
                    content="Your delivery content here...",
                    slug="delivery"
                )
            # Добавьте другие варианты для различных страниц

        return instance

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
