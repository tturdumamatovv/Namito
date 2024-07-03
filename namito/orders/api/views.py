from rest_framework import status, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView

from namito.orders.api.serializers import (
    CartSerializer,
    OrderSerializer,
    OrderHistorySerializer,
    CartItemSerializer,
    CartItemCreateUpdateSerializer,
    OrderListSerializer,
    MultiCartItemAddSerializer
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
        variant_id = self.request.data.get('product_variant')

        # Check if the CartItem with the same product_variant already exists in the cart
        cart_item = CartItem.objects.filter(cart=cart, product_variant_id=variant_id).first()

        if cart_item:
            # If it exists, increase the quantity
            cart_item.quantity += self.request.data.get('quantity', 1)
            cart_item.save()
        else:
            # If it does not exist, create a new CartItem
            serializer.save(cart=cart, product_variant_id=variant_id)


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
            return Response({"error": "Данные запроса должны быть JSON-объектом с ключом 'items'."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Получаем данные элементов
        items_data = request.data.get('items', [])

        # Если items_data не список, возвращаем ошибку
        if not isinstance(items_data, list):
            return Response({"error": "Ключ 'items' должен содержать список элементов."},
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
                    # Проверяем наличие достаточного количества товара на складе
                    product_variant = serializer.validated_data.get('product_variant', cart_item.product_variant)
                    new_quantity = serializer.validated_data.get('quantity', cart_item.quantity)

                    if new_quantity > product_variant.stock:
                        results["errors"].append({
                            "id": item_id,
                            "errors": {"quantity": ["Недостаточно товара на складе."]}
                        })
                        continue

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
                    "errors": {"id": "Элемент корзины с id {} не существует.".format(item_id)}
                })

        # Если есть ошибки, возвращаем статус 400
        if results["errors"]:
            return Response(results, status=status.HTTP_400_BAD_REQUEST)

        # Если все элементы обновлены успешно, возвращаем статус 200
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
        instance.cancel_order()

        # Возвращаем сериализованные данные обновленного заказа
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MultiCartItemAddAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        cart, created = Cart.objects.get_or_create(user=user)

        items_data = request.data.get('items', [])

        # Validate the input data
        serializer = MultiCartItemAddSerializer(data=items_data, many=True)
        serializer.is_valid(raise_exception=True)

        for item_data in serializer.validated_data:
            variant_id = item_data['product_variant']
            quantity = item_data['quantity']

            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product_variant_id=variant_id,
                defaults={'quantity': quantity}
            )
            if not created:
                new_quantity = cart_item.quantity + quantity
                if new_quantity > cart_item.product_variant.stock:
                    return Response(
                        {
                            "error": f"Запрашиваемое количество ({new_quantity}) превышает доступное количество на складе ({cart_item.product_variant.stock})."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                cart_item.quantity = new_quantity
                cart_item.save()

        # Serialize the updated cart
        cart_serializer = CartSerializer(cart, context={'request': request})

        return Response(cart_serializer.data, status=status.HTTP_201_CREATED)
