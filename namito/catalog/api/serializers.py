import math

from django.db import models
from django.db.models import Avg, Min, Q, Case, When, IntegerField

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
from namito.users.api.serializers import UserProfileSerializer


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    parent = serializers.SerializerMethodField()


    class Meta:
        model = Category
        fields = ['id', 'name', 'type', 'slug', 'image', 'parent', 'order', 'meta_title', 'meta_image',
                  'promotion', 'children', 'background_color', 'icon']

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
    colors = serializers.SerializerMethodField()
    brands = serializers.SerializerMethodField()
    sizes = serializers.SerializerMethodField()
    ratings = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()
    max_price = serializers.SerializerMethodField()

    class Meta(CategorySerializer.Meta):
        fields = CategorySerializer.Meta.fields + ['products', 'ratings', 'min_price', 'max_price',
                                                   'brands', 'colors', 'sizes']

    def get_products(self, obj):
        def get_all_products(category):
            products = list(category.products.filter(variants__isnull=False).distinct())
            for child in category.children.all():
                products.extend(get_all_products(child))
            return products

        products = get_all_products(obj)
        products_with_images = [product for product in products if Image.objects.filter(product=product).exists()]
        product_data = []

        for product in products_with_images:
            rating = product.get_popularity_score()  # Получаем рейтинг продукта
            product_serializer = ProductListSerializer(product, context=self.context)
            product_data.append({**product_serializer.data, 'popularity_score': rating})

        return product_data

    def get_min_price(self, obj):
        products = Product.objects.filter(category=obj)
        min_prices = []
        for product in products:
            min_price = product.min_price
            if min_price > 0:  # Учитываем только ненулевые минимальные цены
                min_prices.append(min_price)
        return min(min_prices) if min_prices else None

    def get_max_price(self, obj):
        products = Product.objects.filter(category=obj)
        max_prices = []
        for product in products:
            max_price = product.max_price
            max_prices.append(max_price)
        return max(max_prices) if max_prices else None

    def get_colors(self, obj):
        def get_all_products(category):
            products = list(category.products.filter(variants__isnull=False).distinct())
            for child in category.children.all():
                products.extend(get_all_products(child))
            return products

        products = get_all_products(obj)
        variants = Variant.objects.filter(product__in=products).select_related('color')
        colors = {variant.color for variant in variants if variant.color}

        data = [{'id': color.id, 'name': color.name, 'color': color.color} for color in colors]
        return data

    def get_brands(self, obj):
        def get_all_products(category):
            products = list(category.products.filter(variants__isnull=False).distinct())
            for child in category.children.all():
                products.extend(get_all_products(child))
            return products

        products = get_all_products(obj)
        brands = Brand.objects.filter(products__in=products).distinct()
        data = [{'name': brand.name} for brand in brands]
        return data

    def get_sizes(self, obj):
        def get_all_products(category):
            products = list(category.products.filter(variants__isnull=False).distinct())
            for child in category.children.all():
                products.extend(get_all_products(child))
            return products

        products = get_all_products(obj)
        variants = Variant.objects.filter(product__in=products).select_related('size')
        sizes = {variant.size for variant in variants if variant.size}

        data = [{'id': size.id, 'name': size.name} for size in sizes]
        return data

    def get_ratings(self, obj):
        def get_all_products(category):
            products = list(category.products.filter(variants__isnull=False).distinct())
            for child in category.children.all():
                products.extend(get_all_products(child))
            return products

        products = get_all_products(obj)
        ratings = [math.floor(product.get_average_rating()) for product in products if product.get_average_rating() > 0]
        return set(ratings)


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


class ProductSeoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'meta_title', 'meta_description', 'meta_image', 'keywords')


class CategorySeoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'slug', 'meta_title', 'meta_description', 'meta_image')


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
        # Получаем самую минимальную цену среди всех вариантов продукта
        min_price = Variant.objects.filter(product=product).aggregate(
            min_price=Min(
                Case(
                    When(discounted_price__isnull=False, then='discounted_price'),
                    default='price',
                    output_field=IntegerField(),
                )
            )
        )['min_price']

        if min_price is not None:
            # Находим первый вариант с минимальной ценой или скидкой
            min_variant = Variant.objects.filter(product=product).filter(
                Q(price=min_price) | Q(discounted_price=min_price)
            ).first()

            if min_variant:
                price = min_variant.price
                discount = min_variant.discounted_price
                return {
                    'price': price,
                    'reduced_price': discount if discount != price else None
                }

        # Возвращаем нулевые значения, если не найдено
        return {'price': 0, 'reduced_price': 0}

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
        images = Image.objects.filter(product=product)[:3]  # Ограничение до трех изображений
        if request is not None:
            return [request.build_absolute_uri(image.image.url) for image in images if image.image]
        return [image.image.url for image in images if image.image]

    def get_characteristics(self, product):
        characteristics = Characteristic.objects.filter(product=product)
        return CharacteristicsSerializer(characteristics, many=True).data

    def to_representation(self, instance):
        if not Image.objects.filter(product=instance).exists():  # Проверка наличия изображений
            return None
        representation = super().to_representation(instance)
        variants = Variant.objects.filter(product=instance)
        representation['variants'] = VariantSerializer(variants, many=True).data
        return representation


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
    rating_count = serializers.SerializerMethodField()
    review_allowed = serializers.SerializerMethodField()
    images = ImageSerializer(many=True, read_only=True)
    category_name = serializers.SerializerMethodField()
    category_slug = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'category', 'category_name', 'category_slug', 'variants', 'average_rating', 'tags', 'brand', 'is_favorite',
                  'cart_quantity', 'sku', 'review_count', 'rating_count', 'characteristics', 'reviews', 'review_allowed', 'images']

    def get_variants(self, product):
        variants_qs = Variant.objects.filter(product=product, product__active=True).order_by('-main', 'price')
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
        reviews_qs = Review.objects.filter(product=product).order_by('-created_at')[:5]
        return ReviewSerializer(reviews_qs, many=True, context=self.context).data

    def get_review_count(self, product):
        review_count = Review.objects.filter(product=product, text__isnull=False, text__gt='').count()
        return review_count

    def get_rating_count(self, product):
        rating_count = Review.objects.filter(product=product).count()
        return rating_count

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

    def get_category_name(self, product):
        return product.category.name

    def get_category_slug(self, product):
        return product.category.slug

    def to_representation(self, instance):
        if not instance.active:
            return None
        return super().to_representation(instance)


class ReviewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewImage
        fields = ['id', 'image', 'main_image']


class ReviewSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.SerializerMethodField()
    images = ReviewImageSerializer(many=True, required=False)
    created_at = serializers.DateTimeField(format='%d.%m.%Y', read_only=True)
    updated_at = serializers.DateTimeField(format='%d.%m.%Y', read_only=True)
    review_allowed = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'product', 'product_name', 'product_image', 'user', 'text', 'created_at', 'updated_at', 'rating', 'images', 'review_allowed']

    def get_product_image(self, obj):
        product = obj.product
        main_image = product.images.filter(main_image=True).first()
        if main_image:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(main_image.image.url)
            return main_image.image.url
        else:
            first_image = product.images.first()
            if first_image:
                request = self.context.get('request')
                if request is not None:
                    return request.build_absolute_uri(first_image.image.url)
                return first_image.image.url
        return None

    def get_review_allowed(self, obj):
        request = self.context.get('request', None)
        if request and request.user.is_authenticated:
            user = request.user
            product = obj.product
            variants = Variant.objects.filter(product=product)
            has_purchased_product = OrderedItem.objects.filter(
                order__user=user,
                product_variant__in=variants,
                order__status=1
            ).exists()
            return has_purchased_product
        return False

    def create(self, validated_data):
        review = Review.objects.create(**validated_data)
        for i in self.context.get('request').FILES.getlist('images'):
            ReviewImage.objects.create(review=review, image=i)
        return review

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if not instance.text:  # Если текст отзыва пустой
            representation.pop('text', None)  # Удаляем поле text из представления
        return representation


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
