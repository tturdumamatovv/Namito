from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q, Max, Count, Min
from django.db import models
from django.http import Http404


from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.filters import OrderingFilter

from drf_yasg.utils import swagger_auto_schema
from modeltranslation.translator import translator

from namito.catalog.models import (
    Category,
    Product,
    Color,
    Size,
    Variant,
    Image,
    Review,
    Favorite,
    SizeChart,
    Brand,
    ProductView
)
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ColorSerializer,
    SizeSerializer,
    VariantSerializer,
    ImageSerializer,

    ReviewSerializer,
    FavoriteSerializer,
    BrandSerializer,
    SizeChartSerializer,
    ProductListSerializer,
    ColorSizeBrandSerializer,
    FavoriteToggleSerializer,
    CategoryBySlugSerializer,
    ProductSeoSerializer,
    CategorySeoSerializer

)
from .pagination import CustomPageNumberPagination
from .filters import ProductFilter
from ...orders.models import OrderedItem


class CategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.filter(parent=None)


class CategoryPromotionListView(generics.ListAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.filter(parent=None, promotion=True)


class BrandListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = BrandSerializer


class BrandDetailView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = BrandSerializer


class ProductListView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ProductFilter
    pagination_class = CustomPageNumberPagination
    ordering_fields = ['name', 'max_discount', 'popularity', 'created_at', 'min_variant_price']
    ordering = ['name']

    def get_queryset(self):
        queryset = Product.objects.annotate(
            max_discount=Max('variants__discount_value'),
            popularity=Count('views'),
            min_variant_price=Min('variants__price')
        ).filter(
            active=True,
            variants__isnull=False
        ).distinct()

        ordering_param = self.request.query_params.get('ordering')
        if ordering_param == 'popularity':
            queryset = queryset.order_by('-popularity')
        elif ordering_param == 'max_discount':
            queryset = queryset.order_by('-max_discount')
        elif ordering_param == '-price':
            queryset = queryset.order_by('-min_variant_price')
        elif ordering_param == 'price':
            queryset = queryset.order_by('min_variant_price')
        elif ordering_param == 'created_at':
            queryset = queryset.order_by('-created_at')
        else:
            queryset = queryset.order_by('name')

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            # Убедитесь, что None значения фильтруются
            data = [item for item in serializer.data if item is not None]
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data = [item for item in serializer.data if item is not None]
        return Response(data)


class TopProductListView(generics.ListAPIView):
    serializer_class = ProductListSerializer

    def get_queryset(self):
        # Сначала фильтруем продукты с изображениями
        queryset = Product.objects.annotate(image_count=models.Count('images')).filter(
            is_top=True,
            image_count__gt=0
        ).distinct()

        # Применяем случайный порядок и срезку
        queryset = queryset.order_by('?')[:15]

        return queryset


class NewProductListView(generics.ListAPIView):
    serializer_class = ProductListSerializer

    def get_queryset(self):
        return Product.objects.filter(
            is_new=True
        ).distinct().order_by('-id')[:15]


class SimilarProductsView(generics.ListAPIView):
    serializer_class = ProductListSerializer

    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        product = get_object_or_404(Product, pk=product_id)
        queryset = Product.objects.filter(
            category=product.category,
        ).exclude(pk=product_id).distinct()[:10]
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, many=True)
        data = [item for item in serializer.data if item is not None]
        return Response(data)


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Http404:
            return Response({"detail": "Продукт не существует."}, status=404)
        user = request.user

        if user.is_authenticated:
            ProductView.objects.get_or_create(product=instance, user=user)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ColorCreateView(generics.CreateAPIView):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer


class ColorDetailView(generics.RetrieveAPIView):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer


class SizeCreateView(generics.ListAPIView):
    queryset = Size.objects.all()
    serializer_class = SizeSerializer


class SizeDetailView(generics.RetrieveAPIView):
    queryset = Size.objects.all()
    serializer_class = SizeSerializer


class VariantListView(generics.ListAPIView):
    serializer_class = VariantSerializer

    def get_queryset(self):
        queryset = Variant.objects.all()
        return queryset


class VariantDetailView(generics.RetrieveAPIView):
    serializer_class = VariantSerializer

    def get_queryset(self):
        queryset = Variant.objects.all()
        return queryset


class ImageCreateView(generics.ListAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer


class ImageDetailView(generics.RetrieveAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer


class UserReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Review.objects.all()
        user = self.request.user
        if user.is_authenticated:
            queryset = queryset.filter(user=user)
        else:
            raise PermissionDenied(detail="Authentication credentials were not provided.")
        return queryset


class ProductReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        product_id = self.kwargs.get('pk')
        queryset = Review.objects.filter(product_id=product_id)
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def list(self, request, *args, **kwargs):
        try:
            product_id = self.kwargs.get('pk')
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"detail": "Продукт с указанным идентификатором не найден."}, status=404)

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response_data = serializer.data

        # Add review_allowed field to the response
        review_allowed = self.get_review_allowed(product)

        return Response({
            'reviews': response_data,
            'review_allowed': review_allowed
        })

    def get_review_allowed(self, product):
        request = self.request
        if request.user.is_authenticated:
            user = request.user
            variants = Variant.objects.filter(product=product)
            has_purchased_product = OrderedItem.objects.filter(
                order__user=user,
                product_variant__in=variants,
                order__status=1
            ).exists()
            return has_purchased_product
        return False


class ReviewCreate(generics.CreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def perform_create(self, serializer):
        user = self.request.user
        product = serializer.validated_data.get('product')

        if not product:
            raise ValidationError("Product is required to create a review.")

        if not self.user_can_review_product(user, product):
            raise PermissionDenied("You must have purchased the product to leave a review.")

        serializer.save(user=user)

    def user_can_review_product(self, user, product):
        variants = Variant.objects.filter(product=product)

        return OrderedItem.objects.filter(
            order__user=user,
            product_variant__in=variants,
            order__status=1
        ).exists()


class ReviewDeleteView(generics.DestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_destroy(self, instance):
        user = self.request.user
        if instance.user != user:
            raise PermissionDenied("You do not have permission to delete this review.")
        instance.delete()


class FavoriteToggleAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(request_body=FavoriteToggleSerializer, responses={200: 'Successfully toggled favorite'})
    def post(self, request, *args, **kwargs):
        user = request.user
        product_id = request.data.get('product_id')

        if not product_id:
            return Response({"error": "Product ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": f"Product with ID {product_id} does not exist."},
                            status=status.HTTP_404_NOT_FOUND)

        favorite, created = Favorite.objects.get_or_create(user=user, product=product)
        if created:
            message = "Added to favorites."
        else:
            favorite.delete()
            message = "Removed from favorites."

        return Response({"message": message}, status=status.HTTP_200_OK)


class FavoriteListView(generics.ListAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Favorite.objects.filter(user=user)


class SizeChartListView(generics.ListAPIView):
    serializer_class = SizeChartSerializer

    def get_queryset(self):
        queryset = SizeChart.objects.all()
        category_id = self.kwargs.get('category_id', None)
        if category_id:
            queryset = queryset.filter(categories__id=category_id)

        # Check if category with specified category_id exists
        if category_id and not queryset.exists():
            raise Http404("Категория не существует")

        return queryset


class CategoryBySlugAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryBySlugSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        queryset = Category.objects.filter(slug=slug)
        if not queryset.exists():
            raise Http404("Категория не существует")
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class CategoryByNameStartsWithAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'name'

    def get_queryset(self):
        name_query = self.request.query_params.get('name', None)

        if name_query:
            queryset = Category.objects.filter(name__icontains=name_query)
        else:
            queryset = Category.objects.all()

        return queryset


class ProductSearchByNameAndBrandAPIView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        language_code = self.request.LANGUAGE_CODE

        search_query = self.request.query_params.get('name')
        brand_query = self.request.query_params.get('brand')

        if search_query is None and brand_query is None:
            return queryset.none()

        filters = Q()

        if search_query:
            product_translation_opts = translator.get_options_for_model(Product)
            for field in product_translation_opts.fields:
                translated_field = f"{field}_{language_code}"
                filters |= Q(**{f"{translated_field}__icontains": search_query})

        if brand_query:
            brand_translation_opts = translator.get_options_for_model(Brand)
            for field in brand_translation_opts.fields:
                translated_field = f"brand__{field}_{language_code}"
                filters |= Q(**{f"{translated_field}__icontains": brand_query})

        queryset = queryset.filter(filters).filter(images__isnull=False).distinct()
        return queryset


class ColorSizeBrandAPIView(generics.ListAPIView):
    serializer_class = ColorSizeBrandSerializer

    def list(self, request, *args, **kwargs):
        colors = Color.objects.all()
        sizes = Size.objects.all()
        brands = Brand.objects.all()
        serializer = self.get_serializer({'colors': colors, 'sizes': sizes, 'brands': brands})
        return Response(serializer.data)


class DiscountAPIView(generics.ListAPIView):
    queryset = Product.objects.filter(variants__discount_value__isnull=False,
                                      variants__discount_type__isnull=False).distinct()
    serializer_class = ProductListSerializer

    def list(self, request, *args, **kwargs):
        # Получаем исходный список сериализованных объектов
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        # Исключаем объекты, в которых все поля null
        cleaned_data = [item for item in serializer.data if item is not None]

        return Response(cleaned_data)


class ProductSeoAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSeoSerializer
    lookup_field = 'pk'

    def get_object(self):
        pk = self.kwargs.get('pk')
        try:
            return self.get_queryset().get(pk=pk)
        except Product.DoesNotExist:
            raise Http404("Продукт не существует")


class CategorySeoAPIView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySeoSerializer
    lookup_field = 'slug'

    def get_object(self):
        slug = self.kwargs.get('slug')
        try:
            return self.get_queryset().get(slug=slug)
        except Category.DoesNotExist:
            raise Http404("Категория не существует")
