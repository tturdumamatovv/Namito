from django_filters.rest_framework import DjangoFilterBackend
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_yasg.utils import swagger_auto_schema

from namito.catalog.models import (
    Category,
    Product,
    Color,
    Size,
    Variant,
    Image,
    Review,
    Rating,
    Favorite,
    SizeChart,
    StaticPage,
    MainPage,
    Brand
    )
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ColorSerializer,
    SizeSerializer,
    VariantSerializer,
    ImageSerializer,
    RatingSerializer,
    ReviewSerializer,
    FavoriteSerializer,
    BrandSerializer,
    SizeChartSerializer,
    ProductListSerializer,
    StaticPageSerializer,
    MainPageSerializer,
    AdvertisementSerializer,
    ColorSizeBrandSerializer, FavoriteToggleSerializer

)
from .filters import ProductFilter


class StaticPageDetailView(generics.RetrieveAPIView):
    queryset = StaticPage.objects.all()
    serializer_class = StaticPageSerializer
    lookup_field = 'slug'


class CategoryListView(generics.ListCreateAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.filter(parent=None)


class CategoryPromotionListView(generics.ListAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.filter(parent=None, promotion=True)


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class BrandListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = BrandSerializer


class BrandDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = BrandSerializer


class ProductListView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter


class TopProductListView(generics.ListAPIView):
    queryset = Product.objects.filter(is_top=True).order_by('?')[:15]
    serializer_class = ProductListSerializer


class NewProductListView(generics.ListAPIView):
    queryset = Product.objects.all().order_by('-id')[:15]
    serializer_class = ProductListSerializer


class SimilarProductsView(generics.ListAPIView):
    serializer_class = ProductListSerializer

    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        product = get_object_or_404(Product, pk=product_id)
        queryset = Product.objects.filter(category=product.category).exclude(pk=product_id)[:10]
        return queryset


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class ColorCreateView(generics.CreateAPIView):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer


class ColorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer


class SizeCreateView(generics.ListCreateAPIView):
    queryset = Size.objects.all()
    serializer_class = SizeSerializer


class SizeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Size.objects.all()
    serializer_class = SizeSerializer


class VariantListView(generics.ListCreateAPIView):
    queryset = Variant.objects.all()
    serializer_class = VariantSerializer


class VariantDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Variant.objects.all()
    serializer_class = VariantSerializer


class ImageCreateView(generics.ListCreateAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer


class ImageDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer


class UserReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        queryset = Review.objects.all()
        user_id = self.request.user.id
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        return queryset


class ProductReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        product_id = self.kwargs.get('pk')

        queryset = Review.objects.filter(product_id=product_id)
        return queryset


class ReviewCreate(generics.CreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


class RatingCreate(generics.CreateAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer


class FavoriteToggleAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(request_body=FavoriteToggleSerializer,
                         responses={200: 'Successfully toggled favorite'})
    def post(self, request, *args, **kwargs):
        user = request.user
        product_id = request.data.get('product_id')

        if not product_id:
            return Response({"error": "Product ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        product = Product.objects.get(id=product_id)
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
        return queryset


class MainPageView(generics.ListAPIView):
    queryset = MainPage.objects.all()
    serializer_class = MainPageSerializer


class AdvertisementView(generics.ListAPIView):
    queryset = MainPage.objects.all()
    serializer_class = AdvertisementSerializer


class CategoryBySlugAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'

    def get_queryset(self):
        # Получаем значение slug из URL
        slug = self.kwargs.get('slug')
        # Фильтруем категории по заданному slug
        queryset = Category.objects.filter(slug=slug)
        return queryset


class CategoryByNameStartsWithAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'name'

    def get_queryset(self):
        name_query = self.request.query_params.get('name', None)
        if name_query:
            name_query = name_query.lower()
            queryset = Category.objects.annotate(lower_name=Lower('name')).filter(lower_name__startswith=name_query)
        else:
            queryset = Category.objects.none()
        return queryset


class ProductByNameStartsWithAPIView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'name'

    def get_queryset(self):
        name_query = self.request.query_params.get('name', None)
        if name_query:
            name_query = name_query.lower()
            queryset = Product.objects.annotate(lower_name=Lower('name')).filter(lower_name__startswith=name_query)
        else:
            queryset = Product.objects.none()
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
    queryset = Product.objects.filter(variants__discount_value__isnull=False, variants__discount_type__isnull=False).distinct()
    serializer_class = ProductListSerializer
    