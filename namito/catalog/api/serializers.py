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
    Characteristic,
    ReviewImage
    )
from namito.orders.models import CartItem
from namito.users.models import User


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'type', 'slug', 'image', 'parent', 'order', 'meta_title',
                  'meta_description', 'promotion', 'children', 'background_color']

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
        fields = ['name', 'logo']


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['name', 'color']


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ['name', 'description']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['color', 'name']


class ImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = '__all__'

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class VariantSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source='product.name', read_only=True)
    color = ColorSerializer(read_only=True)
    size = SizeSerializer(read_only=True)
    images = serializers.SerializerMethodField()
    price = serializers.IntegerField()
    discounted_price = serializers.SerializerMethodField()
    discount_value = serializers.IntegerField()

    class Meta:
        model = Variant
        fields = ['id', 'color', 'size', 'price', 'discounted_price', 'images', 'stock',
                  'discount_value', 'discount_type', 'main', 'product']

    def get_images(self, variant):
        images_qs = Image.objects.filter(variant=variant).order_by('-main_image')
        return ImageSerializer(images_qs, many=True, context=self.context).data

    @staticmethod
    def get_discounted_price(variant):
        discounted_price = variant.get_price()
        return discounted_price


class ProductListSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    category = serializers.CharField(source='category.name')
    tags = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()
    cart_quantity = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    brand = BrandSerializer(many=False, read_only=True)
    characteristics = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'category', 'price', 'brand', 'average_rating',
                  'tags', 'is_favorite', 'cart_quantity', 'image', 'characteristics']

    def get_price(self, product):
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
        variants = Variant.objects.filter(product=product, stock__gt=0).order_by('-main', 'id')
        for variant in variants:
            image = Image.objects.filter(variant=variant, main_image=True).first()
            if not image:
                image = Image.objects.filter(variant=variant).first()
            if image:
                image_url = base_url + image.image.url if image.image else None
                images_data.append({
                    'variant_id': variant.id,
                    'image_url': image_url
                })
        return images_data

    def get_characteristics(self, product):
        characteristics = Characteristic.objects.filter(product=product)
        return CharacteristicsSerializer(characteristics, many=True).data


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
    brand = BrandSerializer(read_only=True, many=False)
    reviews = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'category', 'variants', 'average_rating', 'tags',
                  'brand', 'is_favorite', 'cart_quantity', 'rating_count', 'review_count', 'characteristics', 'reviews']

    def get_variants(self, product):
        variants_qs = Variant.objects.filter(product=product, stock__gt=0).order_by('-main')
        return VariantSerializer(variants_qs, many=True, context=self.context).data

    def get_average_rating(self, product):
        # Рассчитайте средний рейтинг на основе отзывов
        reviews = Review.objects.filter(product=product)
        average_rating = reviews.aggregate(Avg('rating'))['rating__avg']

        # Если средний рейтинг отсутствует, вернуть 0
        return average_rating if average_rating is not None else 0

    def get_tags(self, product):
        tags_qs = product.tags.all()
        return TagSerializer(tags_qs, many=True).data

    def get_is_favorite(self, obj):
        user = self.context.get('request').user if 'request' in self.context else None
        if user and user.is_authenticated:
            return Favorite.objects.filter(user=user, product=obj).exists()
        return False

    def get_cart_quantity(self, obj):
        user = self.context.get('request').user if 'request' in self.context else None
        if user and user.is_authenticated:
            quantity = CartItem.objects.filter(
                cart__user=user,
                product_variant__product=obj,
                to_purchase=True
            ).aggregate(total_quantity=models.Sum('quantity'))['total_quantity']
            return quantity if quantity else 0
        return 0

    def get_rating_count(self, product):
        count = Rating.objects.filter(product=product).count()
        return count

    def get_characteristics(self, product):
        characteristics = Characteristic.objects.filter(product=product)
        return CharacteristicsSerializer(characteristics, many=True).data

    def get_reviews(self, product):
        reviews_qs = Review.objects.filter(product=product)
        return ReviewSerializer(reviews_qs, many=True, context=self.context).data

    def get_review_count(self, product):
        # Подсчитайте количество отзывов для продукта
        review_count = Review.objects.filter(product=product).count()
        return review_count


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'profile_picture']


class ReviewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewImage
        fields = ['id', 'image', 'main_image']


class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    images = ReviewImageSerializer(many=True, required=False)

    class Meta:
        model = Review
        fields = ['id', 'product', 'user', 'text', 'created_at', 'updated_at', 'rating', 'images']

    def create(self, validated_data):
        review = Review.objects.create(**validated_data)
        for i in self.context.get('request').FILES.getlist('images'):
            ReviewImage.objects.create(review=review, image=i)
        return review


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
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'user', 'product']


class SizeChartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SizeChartItem
        fields = ['size']


class SizeChartSerializer(serializers.ModelSerializer):
    items = SizeChartItemSerializer(many=True, read_only=True, source='sizechartitem_set')

    class Meta:
        model = SizeChart
        fields = ['id', 'name', 'items']


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


class FavoriteToggleSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(help_text="The unique identifier of the product "
                                                    "to be favorited or unfavored.")
