from rest_framework import status, permissions, generics
from rest_framework.response import Response

from namito.orders.api.serializers import (
    CartSerializer,
    OrderSerializer,
    OrderHistorySerializer,
    CartItemSerializer,
    CartItemCreateUpdateSerializer,
    OrderListSerializer
    )
from namito.orders.models import (
    Cart,
    CartItem,
    Order,
    OrderHistory
)


class CartItemCreateAPIView(generics.CreateAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        cart, created = Cart.objects.get_or_create(user=user)
        variant_id = self.request.data.get('product_variant')  # Получаем идентификатор варианта из запроса
        serializer.save(cart=cart, product_variant_id=variant_id)  # Сохраняем товар в корзине


class CartItemDeleteAPIView(generics.RetrieveDestroyAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            user = self.request.user
            return CartItem.objects.filter(cart__user=user)
        else:
            return CartItem.objects.none()


class CartDetailAPIView(generics.RetrieveAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user = self.request.user
        cart, created = Cart.objects.get_or_create(user=user)
        return cart

    def get(self, request, *args, **kwargs):
        cart = self.get_object()
        if cart.items.exists():
            return super().get(request, *args, **kwargs)
        else:
            if self.request.LANGUAGE_CODE == 'ru':
                return Response({"detail": "Карзина пуста"}, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "Cart is empty."}, status=status.HTTP_200_OK)


class MultiCartItemUpdateAPIView(generics.GenericAPIView):
    serializer_class = CartItemCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, *args, **kwargs):
        user = request.user
        cart = Cart.objects.get(user=user)

        # Проверьте, является ли request.data словарем
        if not isinstance(request.data, dict):
            return Response({"error": "Request data should be a JSON object with 'items' key."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Получаем данные элементов
        items_data = request.data.get('items', [])

        # Если items_data не список, возвращаем ошибку
        if not isinstance(items_data, list):
            return Response({"error": "The 'items' key should contain a list of items."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Словарь для хранения результата обновления
        results = {"updated_items": [], "errors": []}

        for item_data in items_data:
            # Получаем id элемента
            item_id = item_data.get('id')

            try:
                # Получаем элемент корзины
                cart_item = CartItem.objects.get(id=item_id, cart=cart)

                # Обновляем элемент
                serializer = self.serializer_class(cart_item, data=item_data, partial=True)

                if serializer.is_valid():
                    serializer.save()
                    results["updated_items"].append(serializer.data)
                else:
                    results["errors"].append({
                        "id": item_id,
                        "errors": serializer.errors
                    })

            except CartItem.DoesNotExist:
                results["errors"].append({
                    "id": item_id,
                    "errors": "CartItem with id {} does not exist.".format(item_id)
                })

        return Response(results, status=status.HTTP_200_OK)


class OrderCreateAPIView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderDetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Order.objects.filter(user=self.request.user)
        else:
            return Order.objects.none()

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class OrderHistoryListAPIView(generics.ListAPIView):
    serializer_class = OrderHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return OrderHistory.objects.filter(user=user) or []


class UserOrderListAPIView(generics.ListAPIView):
    serializer_class = OrderListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(user=user)


class OrderCancelAPIView(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        # Получаем объект заказа
        instance = self.get_object()

        # Проверяем текущий статус заказа
        if instance.status == 1:  # Заказ уже доставлен
            return Response({"detail": "Order cannot be canceled because it has already been delivered."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Отменяем заказ
        instance.status = 2  # Устанавливаем статус "доставка отменена"
        instance.save()

        # Возвращаем товары на склад
        for ordered_item in instance.ordered_items.all():
            variant = ordered_item.product_variant
            variant.stock += ordered_item.quantity
            variant.save()

        # Возвращаем сериализованные данные обновленного заказа
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
