from django.db import models
from django.db.models import Avg

from rest_framework import serializers

from namito.catalog.models import (
    Category,
    Product,
    Color,
    Size,
    Variant,
    Image,
    Rating,
    Review,
    Favorite,
    Brand,
    SizeChartItem,
    SizeChart,
    Tag,
    StaticPage,
    MainPage,
    Advertisement,
    MainPageSlider,
    Characteristic
    )
from namito.orders.models import CartItem


class StaticPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaticPage
        fields = ['title', 'slug', 'content', 'image',
                  'meta_title', 'meta_description', 'created_at', 'updated_at']


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'type', 'slug', 'image', 'parent',
                   'order', 'meta_title', 'meta_description','promotion', 'children']

    def get_fields(self):
        fields = super().get_fields()
        return fields

    def get_children(self, obj):
        if 'serialized_categories' not in self.context:
            self.context['serialized_categories'] = set()
        if obj.id in self.context['serialized_categories']:
            return []
        self.context['serialized_categories'].add(obj.id)

        serializer = CategorySerializer(obj.children.all(), many=True, context=self.context)
        return serializer.data


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = '__all__'


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['color', 'name']


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'


class VariantSerializer(serializers.ModelSerializer):
    color = ColorSerializer(read_only=True)
    size = SizeSerializer(read_only=True)
    images = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    discounted_price = serializers.SerializerMethodField()

    class Meta:
        model = Variant
        fields = ['id', 'color', 'size', 'price', 'discounted_price',
                  'images', 'stock', 'discount_value', 'discount_type', 'main']

    @staticmethod
    def get_images(variant):
        images_qs = Image.objects.filter(variant=variant).order_by('-main')
        return ImageSerializer(images_qs, many=True).data

    @staticmethod
    def get_discounted_price(variant):
        discounted_price = variant.get_price()
        return discounted_price

    @staticmethod
    def get_price(variant):
        price = variant.get_price()
        return price


class ProductListSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    category = serializers.CharField(source='category.name')
    tags = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()
    cart_quantity = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'category', 'price',
                  'average_rating', 'tags', 'is_favorite', 'cart_quantity', 'image']

    def get_price(self, product):
        # Fetch the main variant; if it's not there, fetch any variant
        main_variant = Variant.objects.filter(product=product, main=True).first()
        if not main_variant:
            main_variant = Variant.objects.filter(product=product).first()

        if main_variant:
            price = main_variant.price

            discount = main_variant.get_price()

            return {
                'price': price,
                'reduced_price': discount
            }

        return {'price': 0, 'discount': 0}

    def get_average_rating(self, product):
        average = Rating.objects.filter(product=product).aggregate(Avg('score'))['score__avg']
        if average is None:
            return 0
        return round(average, 2)

    def get_tags(self, product):
        tags_qs = product.tags.all()
        return TagSerializer(tags_qs, many=True).data

    def get_is_favorite(self, product):
        user = self.context.get('request').user if 'request' in self.context else None

        if user and user.is_authenticated:
            return Favorite.objects.filter(user=user, product=product).exists()
        return False

    def get_cart_quantity(self, product):
        user = self.context.get('request').user if 'request' in self.context else None

        if user and user.is_authenticated:
            quantity = CartItem.objects.filter(
                cart__user=user,
                product_variant__product=product,
                to_purchase=True
            ).aggregate(total_quantity=models.Sum('quantity'))['total_quantity']

            return quantity if quantity else 0
        return 0

    def get_image(self, product):
        base_url = self.context.get('request').build_absolute_uri('/')
        images_data = []

        # Сортируем варианты по признаку главного, затем по ID
        variants = Variant.objects.filter(product=product).order_by('-main', 'id')

        for variant in variants:
            # Пытаемся найти главное изображение варианта
            image = Image.objects.filter(variant=variant, main_image=True).first()
            # Если главного изображения нет, берем первое попавшееся
            if not image:
                image = Image.objects.filter(variant=variant).first()
            # Если изображение есть, добавляем его в результат
            if image:
                image_url = base_url + image.image.url if image.image else None
                images_data.append({
                    'variant_id': variant.id,
                    'image_url': image_url
                })

        # Возвращаем список изображений, по одному на каждый вариант
        return images_data

class CharacteristicsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Characteristic
        fields = ('key', 'value')


class ProductSerializer(serializers.ModelSerializer):
    variants = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()
    cart_quantity = serializers.SerializerMethodField()
    rating_count = serializers.SerializerMethodField()
    characteristics = CharacteristicsSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'category', 'variants', 'average_rating',
                  'tags', 'is_favorite', 'cart_quantity', 'rating_count', 'characteristics']

    def get_variants(self, product):
        variants_qs = Variant.objects.filter(product=product).order_by('-main')
        return VariantSerializer(variants_qs, many=True).data

    def get_average_rating(self, product):
        average = Rating.objects.filter(product=product).aggregate(Avg('score'))['score__avg']
        if average is None:
            return 0
        return round(average, 2)

    def get_tags(self, product):
        tags_qs = product.tags.all()
        return TagSerializer(tags_qs, many=True).data

    def get_is_favorite(self, obj):
        user = self.context.get('request').user if 'request' in self.context else None

        if user and user.is_authenticated:
            return Favorite.objects.filter(user=user, product=obj).exists()
        return False

    def get_cart_quantity(self, obj):
        # Check if 'request' is in the context and thus the user
        user = self.context.get('request').user if 'request' in self.context else None

        if user and user.is_authenticated:
            # Aggregate the quantities of this product in the user's cart(s)
            quantity = CartItem.objects.filter(
                cart__user=user,
                product_variant__product=obj,
                to_purchase=True  # Assuming you want to count only items marked for purchase
            ).aggregate(total_quantity=models.Sum('quantity'))['total_quantity']

            return quantity if quantity else 0
        return 0

    def get_rating_count(self, product):
        count = Rating.objects.filter(product=product).count()
        return count


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'product', 'user', 'text', 'created_at', 'updated_at']


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['id', 'product', 'user', 'score', 'created_at']

    def create(self, validated_data):
        rating, created = Rating.objects.update_or_create(
            product=validated_data.get('product'),
            user=validated_data.get('user'),
            defaults={'score': validated_data.get('score')}
        )
        return rating

    def update(self, instance, validated_data):
        instance.score = validated_data.get('score', instance.score)
        instance.save()
        return instance


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'


class SizeChartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SizeChartItem
        fields = ['size']


class SizeChartSerializer(serializers.ModelSerializer):
    items = SizeChartItemSerializer(many=True, read_only=True, source='sizechartitem_set')

    class Meta:
        model = SizeChart
        fields = ['id', 'name', 'items']


class AdvertisementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertisement
        fields = ["image", 'title', 'description', 'button_link', 'button', 'page']


class MainPageSliderSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = MainPageSlider
        fields = ['title', 'description', 'image', 'link']

    def get_image(self, slider):
        request = self.context.get('request')
        if request is not None:
            return request.build_absolute_uri(slider.image.url)
        else:
            return slider.image.url


class MainPageSerializer(serializers.ModelSerializer):
    slider = serializers.SerializerMethodField()

    class Meta:
        model = MainPage
        fields = ['banner1', 'banner2', 'banner3', 'title', 'description', 'counter1_title',
                   'counter1_value', 'counter2_title', 'counter2_value', 'counter3_title',
                     'counter3_value', 'button_link', 'button', 'slider']

    def get_slider(self, page):
        slider_qs = MainPageSlider.objects.filter(page=page)
        return MainPageSliderSerializer(slider_qs, many=True, context=self.context).data


class ColorSizeBrandSerializer(serializers.Serializer):
    colors = serializers.SerializerMethodField()
    sizes = serializers.SerializerMethodField()
    brands = serializers.SerializerMethodField()

    def get_colors(self, instance):
        colors = Color.objects.all()
        return ColorSerializer(colors, many=True).data

    def get_sizes(self, instance):
        sizes = Size.objects.all()
        return SizeSerializer(sizes, many=True).data

    def get_brands(self, instance):
        brands = Brand.objects.all()
        return BrandSerializer(brands, many=True).data
