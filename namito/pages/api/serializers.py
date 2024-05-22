from rest_framework import serializers

from namito.catalog.api.serializers import ProductSerializer, ProductListSerializer
from namito.catalog.models import Product, Category
from namito.pages.models import (
    MainPageSlider,
    MainPage,
    StaticPage, Phone, Email, SocialLink, Contacts
)
from namito.advertisement.api.serializers import AdvertisementSerializer
from namito.advertisement.models import Advertisement


class MainPageSliderSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = MainPageSlider
        fields = ['title', 'description', 'image', 'link']

    def get_image(self, slider):
        if slider.image and slider.image.file:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(slider.image.url)
            else:
                return slider.image.url
        return None


class MainPageSerializer(serializers.ModelSerializer):
    slider = serializers.SerializerMethodField()
    advertisement = serializers.SerializerMethodField()
    top_products = serializers.SerializerMethodField()

    class Meta:
        model = MainPage
        fields = ['banner1', 'banner2', 'banner3', 'title', 'description', 'counter1_title',
                  'counter1_value', 'counter2_title', 'counter2_value', 'counter3_title',
                  'counter3_value', 'button_link', 'button', 'slider', 'advertisement', 'top_products']

    def get_advertisement(self, page):
        slider_qs = Advertisement.objects.filter(page=page)
        return AdvertisementSerializer(slider_qs, many=True, context=self.context).data

    def get_slider(self, page):
        slider_qs = MainPageSlider.objects.filter(page=page)
        return MainPageSliderSerializer(slider_qs, many=True, context=self.context).data

    def get_top_products(self, page):
        products = Product.objects.filter(is_top=True, variants__stock__gt=0).distinct().order_by('?')[:15]
        serializer = ProductListSerializer(products, many=True, read_only=True,
                                           context={'request': self.context['request']})
        return serializer.data


class StaticPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaticPage
        fields = ['title', 'slug', 'content', 'image', 'meta_title',
                  'meta_description', 'created_at', 'updated_at']


class ContactsSerializer(serializers.ModelSerializer):
    phones = serializers.SerializerMethodField()
    emails = serializers.SerializerMethodField()
    social_links = serializers.SerializerMethodField()
    promoted_categories = serializers.SerializerMethodField()

    class Meta:
        model = Contacts
        fields = ['id', 'phones', 'emails', 'social_links', 'promoted_categories']

    def get_phones(self, obj):
        phones = Phone.objects.all()
        data = [{'phone': phone.phone} for phone in phones]
        return data

    def get_emails(self, obj):
        emails = Email.objects.all()
        data = [{'email': email.email} for email in emails]
        return data

    def get_social_links(self, obj):
        social_links = SocialLink.objects.all()
        data = [{'link': social_link.link, 'icon': social_link.icon} for social_link in social_links]
        return data

    def get_promoted_categories(self, obj):
        categories = Category.objects.filter(promotion=True)
        data = [{'name': category.name, 'slug': category.slug} for category in categories]
        return data
