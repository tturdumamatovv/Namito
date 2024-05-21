from rest_framework import serializers

from namito.catalog.api.serializers import ProductSerializer
from namito.catalog.models import Product
from namito.pages.models import (
    MainPageSlider,
    MainPage,
    StaticPage
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
                  'counter3_value', 'button_link', 'button', 'slider', 'advertisement',]

    def get_advertisement(self, page):
        slider_qs = Advertisement.objects.filter(page=page)
        return AdvertisementSerializer(slider_qs, many=True, context=self.context).data

    def get_slider(self, page):
        slider_qs = MainPageSlider.objects.filter(page=page)
        return MainPageSliderSerializer(slider_qs, many=True, context=self.context).data

    # def get_top_products(self, page):
    #     products = Product.objects.filter(is_top=True, variants__stock__gt=0).distinct().order_by('?')[:15]
    #     serializer = ProductSerializer(products, many=True)
    #     return serializer.data


class StaticPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaticPage
        fields = ['title', 'slug', 'content', 'image', 'meta_title',
                  'meta_description', 'created_at', 'updated_at']
