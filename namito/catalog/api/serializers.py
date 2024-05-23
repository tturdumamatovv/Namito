from django.db import models
from django.db.models import Avg
from django.conf import settings

from rest_framework import serializers

from namito.catalog.models import (
    Category,
    Product,
    Color,
    Size,
    Variant,
    Image,
    Review,
    Favorite,
    Brand,
    SizeChartItem,
    SizeChart,
    Tag,
    Characteristic,
    ReviewImage
)
from namito.orders.models import CartItem, OrderedItem
from namito.users.models import User


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    brands = serializers.SerializerMethodField()
    sizes = serializers.SerializerMethodField()
    parent = serializers.SerializerMethodField()
    colors = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'type', 'slug', 'image', 'parent', 'order', 'meta_title',
                  'meta_description', 'promotion', 'children', 'background_color', 'brands', 'sizes', 'colors']

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

    def get_brands(self, obj):
        brands = Brand.objects.filter(categories=obj)
        data = [{'name': brand.name, 'logo': brand.logo.url if brand.logo else None} for brand in brands]
        return data

    def get_sizes(self, obj):
        sizes = Size.objects.filter(categories=obj)
        size_data = [{'id': size.id, 'name': size.name} for size in sizes]
        return size_data

    def get_colors(self, obj):
        colors = Color.objects.all()
        data = [{'id': color.id, 'name': color.name, 'color': color.color} for color in colors]
        return data

    def get_parent(self, obj):
        if obj.parent:
            return {
                'id': obj.parent.id,
                'name': obj.parent.name,
                'slug': obj.parent.slug
            }
        return None


class CategoryBySlugSerializer(CategorySerializer):
    products = serializers.SerializerMethodField()

    class Meta(CategorySerializer.Meta):
        fields = CategorySerializer.Meta.fields + ['products']

    def get_products(self, obj):
        def get_all_products(category):
            products = list(category.products.all())
            for child in category.children.all():
                products.extend(get_all_products(child))
            return products

        products = get_all_products(obj)
        serializer = ProductListSerializer(products, many=True, context=self.context)
        return serializer.data


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['name', 'logo']


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['id', 'name', 'color']


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ['id', 'name', 'description']


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
    price = serializers.IntegerField()
    discounted_price = serializers.SerializerMethodField()
    discount_value = serializers.IntegerField()

    class Meta:
        model = Variant
        fields = ['id', 'color', 'size', 'price', 'discounted_price', 'stock',
                  'discount_value', 'discount_type', 'main', 'product']

    @staticmethod
    def get_discounted_price(variant):
        discounted_price = variant.get_price()
        return discounted_price if discounted_price != variant.price else None


class ProductListSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    category = serializers.CharField(source='category.name')
    tags = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()
    cart_quantity = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    brand = BrandSerializer(many=False, read_only=True)
    characteristics = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'category', 'price', 'brand', 'average_rating', 'tags', 'is_favorite',
                  'cart_quantity', 'images', 'characteristics']

    def get_price(self, product):
        main_variant = Variant.objects.filter(product=product, main=True).first()
        if not main_variant:
            main_variant = Variant.objects.filter(product=product).first()
        if main_variant:
            price = main_variant.price
            discount = main_variant.get_price()
            return {
                'price': price,
                'reduced_price': discount if discount != price else None
            }
        return {'price': 0, 'discount': 0}

    def get_average_rating(self, product):
        average = Review.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']
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

    def get_images(self, product):
        request = self.context.get('request')
        images = Image.objects.filter(product=product)
        if request is not None:
            return [request.build_absolute_uri(image.image.url) for image in images if image.image]
        return [image.image.url for image in images if image.image]

    def get_characteristics(self, product):
        characteristics = Characteristic.objects.filter(product=product)
        return CharacteristicsSerializer(characteristics, many=True).data

    def to_representation(self, instance):
        if not instance.active:
            return None
        return super().to_representation(instance)


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
    characteristics = CharacteristicsSerializer(many=True, read_only=True)
    brand = BrandSerializer(read_only=True, many=False)
    reviews = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    review_allowed = serializers.SerializerMethodField()
    images = ImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'category', 'variants', 'average_rating', 'tags', 'brand', 'is_favorite',
                  'cart_quantity', 'sku', 'review_count', 'characteristics', 'reviews', 'review_allowed', 'images']

    def get_variants(self, product):
        variants_qs = Variant.objects.filter(product=product, stock__gt=0, product__active=True).order_by('-main')
        return VariantSerializer(variants_qs, many=True, context=self.context).data

    def get_average_rating(self, product):
        average = Review.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']
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
        user = self.context.get('request').user if 'request' in self.context else None
        if user and user.is_authenticated:
            quantity = CartItem.objects.filter(
                cart__user=user,
                product_variant__product=obj,
                to_purchase=True
            ).aggregate(total_quantity=models.Sum('quantity'))['total_quantity']
            return quantity if quantity else 0
        return 0

    def get_characteristics(self, product):
        characteristics = Characteristic.objects.filter(product=product)
        return CharacteristicsSerializer(characteristics, many=True).data

    def get_reviews(self, product):
        reviews_qs = Review.objects.filter(product=product).order_by('-created_at')[:3]
        return ReviewSerializer(reviews_qs, many=True, context=self.context).data

    def get_review_count(self, product):
        review_count = Review.objects.filter(product=product).count()
        return review_count

    def get_review_allowed(self, product):
        user = self.context.get('request').user
        if user.is_authenticated:
            variants = Variant.objects.filter(product=product)
            has_purchased_product = OrderedItem.objects.filter(
                order__user=user,
                product_variant__in=variants,
                order__status=1
            ).exists()
            return has_purchased_product
        return False

    def get_images(self, product):
        request = self.context.get('request')
        images = Image.objects.filter(product=product)
        if request is not None:
            return [request.build_absolute_uri(image.image.url) for image in images if image.image]
        return [image.image.url for image in images if image.image]

    def to_representation(self, instance):
        if not instance.active:
            return None
        return super().to_representation(instance)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'full_name', 'profile_picture']


class ReviewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewImage
        fields = ['id', 'image', 'main_image']


class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    images = ReviewImageSerializer(many=True, required=False)
    created_at = serializers.DateTimeField(format='%d.%m.%Y', read_only=True)
    updated_at = serializers.DateTimeField(format='%d.%m.%Y', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'product', 'user', 'text', 'created_at', 'updated_at', 'rating', 'images']

    def create(self, validated_data):
        review = Review.objects.create(**validated_data)
        for i in self.context.get('request').FILES.getlist('images'):
            ReviewImage.objects.create(review=review, image=i)
        return review


class FavoriteSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)

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
