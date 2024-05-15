from django.contrib import admin

from .models import (
    Cart,
    CartItem,
    Order,
    OrderHistory, OrderedItem
)


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    show_change_link = True


class OrderedItemInline(admin.TabularInline):
    model = OrderedItem
    extra = 0
    show_change_link = True


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at']
    inlines = [CartItemInline]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'payment_status', 'total_amount', 'created_at']
    inlines = [OrderedItemInline]

