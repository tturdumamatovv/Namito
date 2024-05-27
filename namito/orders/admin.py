from django.contrib import admin

from .models import (
    Cart,
    CartItem,
    Order,
    OrderHistory, OrderedItem
)


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1
    show_change_link = True
    readonly_fields = [
        'cart',
        'product_variant',
        'quantity',
        'to_purchase',
        'order',
    ]


class OrderHistoryInline(admin.TabularInline):
    model = OrderHistory
    extra = 1
    show_change_link = True


class OrderedItemInline(admin.TabularInline):
    model = OrderedItem
    extra = 0
    show_change_link = True
    readonly_fields = [
        'order',
        'product_variant',
        'quantity',
    ]


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at']
    inlines = [CartItemInline]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'payment_status', 'total_amount', 'created_at']
    readonly_fields = [
        'user',
        'cart',
        'total_amount',
        'created_at',
        'finished_at',
        'delivery_method',
        'user_address',
        'payment_method',
        'order_number',
    ]
    inlines = [OrderedItemInline]

