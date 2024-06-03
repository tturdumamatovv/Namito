from rest_framework import generics
from rest_framework.response import Response

from django.shortcuts import get_object_or_404

from namito.pages.api.serializers import MainPageSerializer, StaticPageSerializer, ContactsSerializer, LayoutSeoSerializer
from namito.pages.models import MainPage, StaticPage, Contacts, MainPageLayoutMeta
from namito.pages.api import pages_default_texts


class MainPageView(generics.RetrieveAPIView):
    serializer_class = MainPageSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_object(self):
        instance = None
        try:
            instance = MainPage.objects.get(pk=1)
        except:
            instance = MainPage.objects.create(
                title='black Friday in NAMITO',
                title_en='black Friday in NAMITO',
                title_ru='черная пятница в NAMITO',
                description='Have a chance to purchase items at 70 percent off',
                description_en='Have a chance to purchase items at 70 percent off',
                description_ru='Успейте приобрести товары с 70 процентной скидкой',
                counter1_title='Foreign brands',
                counter1_title_en='Foreign brands',
                counter1_title_ru='Зарубежных брендов',
                counter1_value='200+',
                counter2_title='Quality goods',
                counter2_title_en='Quality goods',
                counter2_title_ru='Качественных товаров',
                counter2_value='2000+',
                counter3_value='5000+',
                counter3_title='Happy customers',
                counter3_title_en='Happy customers',
                counter3_title_ru='Счастливых покупателей',
                button_link='#',
                button='View discounted items',
                button_en='View discounted items',
                button_ru='Смотреть товары со скидкой',
            )

        return instance

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


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
                    title=pages_default_texts.DELIVERY_TITLE_EN,
                    title_ru=pages_default_texts.DELIVERY_TITLE_RU,
                    title_en=pages_default_texts.DELIVERY_TITLE_EN,

                    content=pages_default_texts.DELIVERY_CONTENT_EN,
                    content_ru=pages_default_texts.DELIVERY_CONTENT_RU,
                    content_en=pages_default_texts.DELIVERY_CONTENT_EN,
                    slug="delivery"
                )

        return instance

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class LayoutView(generics.RetrieveAPIView):
    serializer_class = ContactsSerializer

    def get_object(self):
        # Получаем первый объект Contacts или вызываем 404 ошибку, если объект не найден
        instance = get_object_or_404(Contacts.objects.all())

        return instance

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class LayoutSeoAPIView(generics.ListAPIView):
    queryset = MainPageLayoutMeta.objects.all()
    serializer_class = LayoutSeoSerializer
