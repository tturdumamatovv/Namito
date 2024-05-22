from django.urls import path
from django.views.generic import TemplateView

from namito.catalog.api.views import (
    CategoryListView,
    ProductListView,
    ProductDetailView,
    ColorCreateView,
    ColorDetailView,
    SizeCreateView,
    SizeDetailView,
    VariantListView,
    VariantDetailView,
    ImageCreateView,
    ImageDetailView,
    ReviewCreate,
    FavoriteToggleAPIView,
    FavoriteListView,
    BrandListView,
    BrandDetailView,
    CategoryPromotionListView,
    SizeChartListView,
    UserReviewListView,
    TopProductListView,
    NewProductListView,
    CategoryBySlugAPIView,
    CategoryByNameStartsWithAPIView,
    ProductSearchByNameAndBrandAPIView,
    ColorSizeBrandAPIView,
    ProductReviewListView,
    SimilarProductsView,
    DiscountAPIView
    )


category_patterns = [
    path('categories/', CategoryListView.as_view()),
    path('categories/promotion/', CategoryPromotionListView.as_view()),
    path('brands/', BrandListView.as_view()),
    path('brands/<int:pk>/', BrandDetailView.as_view()),
    path('category/<slug:slug>/', CategoryBySlugAPIView.as_view(), name='category-detail'),
    path('categories/startswith/', CategoryByNameStartsWithAPIView.as_view(), name='category_startswith'),
]

product_patterns = [
    path('products/', ProductListView.as_view()),
    path('top-products/', TopProductListView.as_view()),
    path('discounts/', DiscountAPIView.as_view(), name='discounts'),
    path('new-products/', NewProductListView.as_view()),
    path('products/<int:pk>/', ProductDetailView.as_view()),
    path('products/search/', ProductSearchByNameAndBrandAPIView.as_view(), name='product_startswith'),
    path('products/<int:pk>/reviews/', ProductReviewListView.as_view(), name='product-reviews'),
    path('products/<int:product_id>/similar/', SimilarProductsView.as_view(), name='similar-products'),
]

entity_patterns = [
    path('colors-sizes-brands/', ColorSizeBrandAPIView.as_view(), name='colors-sizes-brands'),
    path('color/', ColorCreateView.as_view()),
    path('color/<int:pk>/', ColorDetailView.as_view()),
    path('size/', SizeCreateView.as_view()),
    path('size/<int:pk>/', SizeDetailView.as_view()),
    path('variants/', VariantListView.as_view()),
    path('variants/<int:pk>/', VariantDetailView.as_view()),
    path('images/', ImageCreateView.as_view()),
    path('images/<int:pk>/', ImageDetailView.as_view()),
    path('reviews/', ReviewCreate.as_view()),
    path('reviews-list/', UserReviewListView.as_view(), name='user_reviews'),
]

utility_patterns = [
    path('favorite/toggle/', FavoriteToggleAPIView.as_view(), name='favorite-toggle'),
    path('favorites/', FavoriteListView.as_view(), name='favorite-list'),
    path('size-charts/', SizeChartListView.as_view(), name='size-chart-list'),
    path('size-charts/<int:category_id>/', SizeChartListView.as_view(), name='size-chart-list-by-category'),

]

urlpatterns = [
    *category_patterns,
    *product_patterns,
    *entity_patterns,
    *utility_patterns,
]

