from namito.catalog.api.serializers import VariantSerializer
from namito.orders.models import (
    Cart,
    CartItem,
    Order,
    OrderHistory,
    OrderedItem
    )
from namito.users.models import UserAddress
from namito.users.api.serializers import UserAddressDetailSerializer

from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from django.db import transaction


class CartItemCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product_variant', 'quantity', 'to_purchase']

    def validate_product_variant(self, value):
        if value.stock <= 0:
            raise serializers.ValidationError("Товар не доступен для добавления в корзину.")

        return value


class CartItemSerializer(serializers.ModelSerializer):
    product_variant = VariantSerializer(required=False)
    product_name = serializers.CharField(source='product_variant.product.name', read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product_variant', 'quantity', 'to_purchase', 'product_name']


class CartSerializer(ModelSerializer):
    items = CartItemSerializer(many=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'created_at', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        cart = Cart.objects.create(**validated_data)
        for item_data in items_data:
            CartItem.objects.create(cart=cart, **item_data)
        return cart


class OrderedItemSerializer(ModelSerializer):
    product_variant = VariantSerializer()
    product_name = serializers.CharField(source='product_variant.product.name', read_only=True)

    class Meta:
        model = OrderedItem
        fields = ['id', 'product_variant', 'quantity', 'product_name']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderedItemSerializer(many=True, read_only=True, source='ordered_items')
    total_amount = serializers.IntegerField(read_only=True)
    delivery_address = serializers.PrimaryKeyRelatedField(
        queryset=UserAddress.objects.all(), required=False, source='user_address'
    )

    class Meta:
        model = Order
        fields = [
            'id', 'cart', 'total_amount', 'payment_status', 'status', 'created_at', 'finished_at',
            'items', 'delivery_method', 'delivery_address', 'payment_method'
        ]
        read_only_fields = ['cart', 'total_amount', 'created_at', 'finished_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        user_address_serializer = UserAddressDetailSerializer(instance.user_address)
        representation['delivery_address'] = user_address_serializer.data
        return representation

    def create(self, validated_data):
        user = self.context['request'].user
        cart = Cart.objects.get(user=user)

        items_to_purchase = cart.items.filter(to_purchase=True)
        if not items_to_purchase.exists():
            raise serializers.ValidationError("There are no items to purchase in the cart.")

        delivery_method = validated_data.get('delivery_method', 'курьером')
        delivery_address_id = validated_data.get('user_address')  # Using 'user_address' as source

        payment_method = validated_data.get('payment_method', 'картой')

        # Check if delivery address is required
        if delivery_method == 'курьером':
            if not delivery_address_id:
                raise serializers.ValidationError("Delivery address is required for courier delivery.")

            user_address = None
            if delivery_address_id:
                try:
                    user_address = UserAddress.objects.get(id=delivery_address_id, user=user)
                except UserAddress.DoesNotExist:
                    raise serializers.ValidationError(
                        "The provided delivery address does not exist or does not belong to the user.")
            else:
                # Create a new address if none is provided
                address_data = self.context['request'].data.get('delivery_address_data')
                if not address_data:
                    raise serializers.ValidationError("Address data is required to create a new delivery address.")

                user_address_serializer = UserAddressDetailSerializer(data=address_data)
                if user_address_serializer.is_valid(raise_exception=True):
                    user_address = user_address_serializer.save(user=user)

        total_amount = 0

        with transaction.atomic():
            order = Order.objects.create(
                user=user,
                cart=cart,
                total_amount=0,
                delivery_method=delivery_method,
                user_address=user_address,
                payment_method=payment_method
            )

            for item in items_to_purchase:
                price = item.product_variant.get_price()
                total_amount += price * item.quantity

                OrderedItem.objects.create(
                    order=order,
                    product_variant=item.product_variant,
                    quantity=item.quantity
                )

            order.total_amount = total_amount
            order.save()

            items_to_purchase.delete()

        return order

    def update(self, instance, validated_data):
        if 'delivery_method' in validated_data and validated_data['delivery_method'] == 'курьером':
            delivery_address_id = validated_data.get('user_address')
            if delivery_address_id is None:
                raise serializers.ValidationError("Delivery address is required for courier delivery.")

        return super().update(instance, validated_data)


class OrderHistorySerializer(ModelSerializer):
    class Meta:
        model = OrderHistory
        fields = '__all__'


class OrderListSerializer(serializers.ModelSerializer):
    total_amount = serializers.IntegerField()

    class Meta:
        model = Order
        fields = ['id', 'order_number', 'created_at', 'status', 'total_amount']
        read_only_fields = ['id', 'order_number', 'created_at', 'status', 'total_amount']
