from django.urls import path

from namito.orders.api.views import (
    CartDetailAPIView,
    CartItemCreateAPIView,
    CartItemDeleteAPIView,
    OrderCreateAPIView,
    OrderDetailAPIView,
    OrderHistoryListAPIView,
    UserOrderListAPIView,
    MultiCartItemUpdateAPIView,
    OrderCancelAPIView,
    MultiCartItemAddAPIView
    )

urlpatterns = [
    path('add/', CartItemCreateAPIView.as_view(), name='cart-add'),
    path('cart/add-multiple/', MultiCartItemAddAPIView.as_view(), name='add-multiple-cart-items'),
    path('detail/', CartDetailAPIView.as_view(), name='cart-detail'),
    path('item/<int:pk>/', CartItemDeleteAPIView.as_view(), name='cart-item-update-delete'),
    path('multi-update/', MultiCartItemUpdateAPIView.as_view(), name='cart-multi-update'),
    path('orders/create/', OrderCreateAPIView.as_view(), name='order-create'),
    path('orders/<int:pk>/', OrderDetailAPIView.as_view(), name='order-detail'),
    path('orders/<int:pk>/cancel/', OrderCancelAPIView.as_view(), name='order-cancel'),
    path('order-history/', OrderHistoryListAPIView.as_view(), name='order-history-list'),
    path('orders/', UserOrderListAPIView.as_view(), name='user_order_list'),
]
