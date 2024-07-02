from rest_framework import serializers
from django.db.models import OuterRef, Subquery

from namito.catalog.api.serializers import ProductListSerializer
from namito.catalog.models import Product, Category
from namito.pages.models import (
    MainPageSlider,
    MainPage,
    StaticPage, Phone, Email, SocialLink, Contacts, PaymentMethod, FAQ, MainPageLayoutMeta
)
from namito.advertisement.api.serializers import AdvertisementSerializer
from namito.advertisement.models import Advertisement


class MainPageSliderSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    small_image = serializers.SerializerMethodField()

    class Meta:
        model = MainPageSlider
        fields = ['image', 'link', 'small_image']

    def get_image(self, slider):
        if slider.image and slider.image.file:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(slider.image.url)
            else:
                return slider.image.url
        return None

    def get_small_image(self, slider):
        if slider.small_image and slider.small_image.file:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(slider.small_image.url)
            else:
                return slider.small_image.url
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
        # Используем подзапрос для выбора только уникальных продуктов
        subquery = Product.objects.filter(
            id=OuterRef('id'),
            is_top=True,
            variants__stock__gt=0
        ).distinct().order_by('?')[:15]

        products = Product.objects.filter(id__in=Subquery(subquery.values('id')))

        # Сериализуем продукты
        serializer = ProductListSerializer(products, many=True, context={'request': self.context['request']})

        # Убираем None из результатов сериализации
        serialized_data = [product for product in serializer.data if product is not None]

        return serialized_data


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ['question', 'answer']


class StaticPageSerializer(serializers.ModelSerializer):
    faqs = FAQSerializer(many=True, read_only=True)

    class Meta:
        model = StaticPage
        fields = ['title', 'slug', 'content', 'image', 'meta_title',
                  'meta_description', 'created_at', 'updated_at', 'faqs']


class ContactsSerializer(serializers.ModelSerializer):
    phones = serializers.SerializerMethodField()
    emails = serializers.SerializerMethodField()
    social_links = serializers.SerializerMethodField()
    payment_methods = serializers.SerializerMethodField()
    promoted_categories = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()

    class Meta:
        model = Contacts
        fields = ['id', 'phones', 'emails', 'social_links', 'payment_methods', 'promoted_categories', 'categories']

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
        request = self.context.get('request')
        data = [{
            'link': social_link.link,
            'icon': request.build_absolute_uri(social_link.icon.url) if social_link.icon else None
        } for social_link in social_links]
        return data

    def get_payment_methods(self, obj):
        payment_methods = PaymentMethod.objects.all()
        request = self.context.get('request')
        data = [{
            'link': payment_method.link,
            'icon': request.build_absolute_uri(payment_method.icon.url) if payment_method.icon else None
        } for payment_method in payment_methods]
        return data

    def get_promoted_categories(self, obj):
        categories = Category.objects.filter(promotion=True)
        request = self.context.get('request')
        data = [{'name': category.name, 'slug': category.slug, 'icon': request.build_absolute_uri(category.icon.url) if category.icon else None} for category in categories]
        return data

    def get_categories(self, obj):

        def get_nested_categories_data(category):
            request = self.context.get('request')
            category_data = {
                'name': category.name,
                'slug': category.slug,
                'icon': request.build_absolute_uri(category.icon.url) if category.icon else None,
                'children': []
            }
            children_categories = category.children.all()
            for child_category in children_categories:
                child_data = get_nested_categories_data(child_category)
                category_data['children'].append(child_data)
            return category_data

        root_categories = Category.objects.filter(parent__isnull=True)
        categories_data = []
        for root_category in root_categories:
            root_category_data = get_nested_categories_data(root_category)
            categories_data.append(root_category_data)
        return categories_data


class LayoutSeoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainPageLayoutMeta
        fields = ('meta_title', 'meta_description', 'meta_image')
