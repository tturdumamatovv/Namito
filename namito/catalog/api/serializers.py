from rest_framework import serializers
from namito.catalog.models import Category, Product, Color, Size, Variant, Image, Rating, Review, Favorite, Brand, \
    SizeChartItem, SizeChart, Tag
from django.db.models import Avg


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'type', 'slug', 'image', 'parent', 'order', 'meta_title', 'meta_description',
                  'promotion', 'children']

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
    discounted_price = serializers.SerializerMethodField()

    class Meta:
        model = Variant
        fields = ['color', 'size', 'price', 'discounted_price', 'images', 'stock', 'discount_value', 'discount_type']

    @staticmethod
    def get_images(variant):
        images_qs = Image.objects.filter(variant=variant)
        return ImageSerializer(images_qs, many=True).data

    @staticmethod
    def get_discounted_price(variant):
        price = variant.get_price()
        return price


class ProductSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    category = serializers.CharField(source='category.name')
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'category', 'price', 'average_rating', 'tags']

    def get_price(self, product):
        main_variant = Variant.objects.filter(product=product, main=True).first()

        if not main_variant:
            main_variant = Variant.objects.filter(product=product).first()

        if main_variant:
            return VariantSerializer(main_variant).data['price']
        else:
            return None

    def get_average_rating(self, product):
        average = Rating.objects.filter(product=product).aggregate(Avg('score'))['score__avg']
        if average is None:
            return 0
        return round(average, 2)

    def get_tags(self, product):
        tags_qs = product.tags.all()
        return TagSerializer(tags_qs, many=True).data


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
