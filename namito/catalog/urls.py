from django.urls import path

from namito.catalog.api.views import CategoryListView, CategoryDetailView, ProductListView, ProductDetailView, \
    ColorCreateView, \
    ColorDetailView, SizeCreateView, SizeDetailView, VariantListView, VariantDetailView, ImageCreateView, ImageDetailView, \
    ReviewCreate, RatingCreate, FavoriteToggleAPIView, FavoriteListView, BrandListView, \
    BrandDetailView, CategoryPromotionListView, SizeChartListView, UserReviewListView

urlpatterns = [
    path('categories/', CategoryListView.as_view()),
    path('categories/promotion/', CategoryPromotionListView.as_view()),
    path('categories/<int:pk>/', CategoryDetailView.as_view()),
    path('brands/', BrandListView.as_view()),
    path('brands/<int:pk>/', BrandDetailView.as_view()),
    path('products/', ProductListView.as_view()),
    path('products/<int:pk>/', ProductDetailView.as_view()),
    path('colors/', ColorCreateView.as_view()),
    path('colors/<int:pk>/', ColorDetailView.as_view()),
    path('sizes/', SizeCreateView.as_view()),
    path('sizes/<int:pk>/', SizeDetailView.as_view()),
    path('variants/', VariantListView.as_view()),
    path('variants/<int:pk>/', VariantDetailView.as_view()),
    path('images/', ImageCreateView.as_view()),
    path('images/<int:pk>/', ImageDetailView.as_view()),
    path('reviews/', ReviewCreate.as_view()),
    path('reviews/', UserReviewListView.as_view(), name='user_reviews'),

    path('ratings/', RatingCreate.as_view()),
    path('favorite/toggle/', FavoriteToggleAPIView.as_view(), name='favorite-toggle'),
    path('favorites/', FavoriteListView.as_view(), name='favorite-list'),
    path('size-charts/', SizeChartListView.as_view(), name='size-chart-list'),
    path('size-charts/<int:category_id>/', SizeChartListView.as_view(), name='size-chart-list-by-category'),

]
