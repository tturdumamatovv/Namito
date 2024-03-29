from django.urls import path

from namito.orders.api.views import CartDetailAPIView, CartItemCreateAPIView, CartItemUpdateDeleteAPIView, OrderCreateAPIView, OrderDetailAPIView, OrderHistoryListAPIView, UserOrderListAPIView


urlpatterns = [
    path('add/', CartItemCreateAPIView.as_view(), name='cart-add'),
    path('detail/', CartDetailAPIView.as_view(), name='cart-detail'),
    path('item/<int:pk>/', CartItemUpdateDeleteAPIView.as_view(), name='cart-item-update-delete'),
    path('orders/create/', OrderCreateAPIView.as_view(), name='order-create'),
    path('orders/<int:pk>/', OrderDetailAPIView.as_view(), name='order-detail'),
    path('order-history/', OrderHistoryListAPIView.as_view(), name='order-history-list'),
    path('orders/', UserOrderListAPIView.as_view(), name='user_order_list'),
]
