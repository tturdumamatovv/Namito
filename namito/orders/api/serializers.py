from namito.catalog.api.serializers import VariantSerializer
from namito.users.api.serializers import CustomUserSerializer 
from namito.orders.models import Cart, CartItem, Order, OrderHistory, OrderedItem
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from django.db import transaction


class CartItemCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product_variant', 'quantity', 'to_purchase']


class CartItemSerializer(serializers.ModelSerializer):
    product_variant = VariantSerializer(required=False)
    class Meta:
        model = CartItem
        fields = ['id', 'product_variant', 'quantity', 'to_purchase']
        

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

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', [])
        instance.items.all().delete()
        for item_data in items_data:
            CartItem.objects.create(cart=instance, **item_data)
        return instance


class OrderedItemSerializer(ModelSerializer):
    product_variant = VariantSerializer()

    class Meta:
        model = OrderedItem
        fields = ['id', 'product_variant', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderedItemSerializer(many=True, read_only=True, source='ordered_items')
    user = CustomUserSerializer(required=False)

    class Meta:
        model = Order
        fields = ['id', 'user', 'cart', 'total_amount', 'payment_status', 'status', 'created_at', 'finished_at', 'items', 'delivery_method', 'delivery_address', 'payment_method']
        read_only_fields = ['user', 'cart', 'total_amount', 'created_at', 'finished_at']

    def create(self, validated_data):
        user = self.context['request'].user
        cart = Cart.objects.get(user=user)
        
        items_to_purchase = cart.items.filter(to_purchase=True)
        if not items_to_purchase.exists():
            raise serializers.ValidationError("There are no items to purchase in the cart.")

        delivery_method = validated_data.get('delivery_method', 'courier') 
        delivery_address = validated_data.get('delivery_address') 
        payment_method = validated_data.get('payment_method')

        if delivery_method == 'courier' and not delivery_address:
            raise serializers.ValidationError("Delivery address is required for courier delivery.")

        total_amount = 0
        
        with transaction.atomic():
            order = Order.objects.create(
                user=user,
                cart=cart,  
                total_amount=total_amount,
                delivery_method=delivery_method,
                delivery_address=delivery_address,
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
        if 'delivery_method' in validated_data and validated_data['delivery_method'] == 'courier':
            delivery_address = validated_data.get('delivery_address')
            if not delivery_address:
                raise serializers.ValidationError("Delivery address is required for courier delivery.")

        return super().update(instance, validated_data)


class OrderHistorySerializer(ModelSerializer):
    class Meta:
        model = OrderHistory
        fields = '__all__'
