from namito.catalog.api.serializers import VariantSerializer
from namito.catalog.models import Image, Variant
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

    def validate_quantity(self, value):
        product_variant = self.initial_data.get('product_variant') or self.instance.product_variant
        if isinstance(product_variant, int):
            product_variant = Variant.objects.get(pk=product_variant)
        if value > product_variant.stock:
            raise serializers.ValidationError("Недостаточно товара на складе.")
        return value


class CartItemSerializer(serializers.ModelSerializer):
    product_variant = VariantSerializer(required=False)
    product_name = serializers.CharField(source='product_variant.product.name', read_only=True)
    product_image = serializers.SerializerMethodField()  # Добавляем изображение продукта

    class Meta:
        model = CartItem
        fields = ['id', 'product_variant', 'quantity', 'to_purchase', 'product_name', 'product_image']

    def get_product_image(self, obj):
        variant = obj.product_variant
        product = variant.product

        main_image = product.images.filter(main_image=True).first()
        if main_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(main_image.image.url)

        first_image = product.images.first()
        if first_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(first_image.image.url)

        return None


class CartSerializer(ModelSerializer):
    items = CartItemSerializer(many=True)
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'created_at', 'items', 'total_amount']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        cart = Cart.objects.create(**validated_data)
        for item_data in items_data:
            CartItem.objects.create(cart=cart, **item_data)
        return cart

    def get_total_amount(self, obj):
        total_amount = sum(item.quantity * (item.product_variant.discounted_price or item.product_variant.price)
                           for item in obj.items.all())
        return total_amount



class OrderedItemSerializer(ModelSerializer):
    product_variant = VariantSerializer()
    product_name = serializers.CharField(source='product_variant.product.name', read_only=True)
    product_id = serializers.CharField(source='product_variant.product.id', read_only=True)
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = OrderedItem
        fields = ['id', 'product_variant', 'quantity', 'product_name', 'product_id', 'product_image']

    def get_product_image(self, obj):
        variant = obj.product_variant
        product = variant.product

        main_image = product.images.filter(main_image=True).first()
        if main_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(main_image.image.url)

        first_image = product.images.first()
        if first_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(first_image.image.url)

        return None


class OrderSerializer(serializers.ModelSerializer):
    items = OrderedItemSerializer(many=True, read_only=True, source='ordered_items')
    total_amount = serializers.IntegerField(read_only=True)
    user_address = serializers.PrimaryKeyRelatedField(
        queryset=UserAddress.objects.all(), required=False
    )

    class Meta:
        model = Order
        fields = [
            'id', 'cart', 'total_amount', 'payment_status', 'status', 'created_at', 'finished_at',
            'items', 'delivery_method', 'user_address', 'payment_method', 'order_number'
        ]
        read_only_fields = ['cart', 'total_amount', 'created_at', 'finished_at', 'order_number']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        user_address_serializer = UserAddressDetailSerializer(instance.user_address)
        representation['user_address'] = user_address_serializer.data
        return representation

    def validate_user_address(self, value):
        user = self.context['request'].user
        if value.user != user:
            raise serializers.ValidationError("Вы можете использовать только свои собственные адреса.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        cart = Cart.objects.get(user=user)

        items_to_purchase = cart.items.filter(to_purchase=True)
        if not items_to_purchase.exists():
            raise serializers.ValidationError("В корзине нет товаров для покупки.")

        delivery_method = validated_data.get('delivery_method', 'курьером')
        user_address = validated_data.get('user_address')
        payment_method = validated_data.get('payment_method', 'картой')

        if delivery_method == 'курьером' and not user_address:
            raise serializers.ValidationError("Для доставки курьером требуется указать адрес доставки.")

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
            user_address_id = validated_data.get('user_address')
            if user_address_id is None:
                raise serializers.ValidationError("Для доставки курьером требуется указать адрес доставки.")

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


class MultiCartItemAddSerializer(serializers.Serializer):
    product_variant = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

    def validate(self, data):
        from namito.catalog.models import Variant
        variant_id = data['product_variant']
        quantity = data['quantity']

        try:
            variant = Variant.objects.get(pk=variant_id)
        except Variant.DoesNotExist:
            raise serializers.ValidationError("Такого варианта товара не существует.")

        if variant.stock <= 0:
            raise serializers.ValidationError("Вариант товара отсутствует на складе.")

        if quantity > variant.stock:
            raise serializers.ValidationError(f"Запрашиваемое количество ({quantity}) превышает доступное количество на складе ({variant.stock}).")

        return data
