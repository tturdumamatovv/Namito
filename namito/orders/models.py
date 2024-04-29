import random

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.core.exceptions import ValidationError

from namito.catalog.models import Variant
from namito.users.models import User


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart for {self.user}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product_variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)
    to_purchase = models.BooleanField(default=True)
    order = models.ForeignKey('Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='items')

    def subtotal(self):
        return self.product_variant.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product_variant}"


class OrderHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='order_history')
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='order_history')
    order_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order history for {self.user} on {self.order_date}"


class OrderedItem(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='ordered_items')
    product_variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name='ordered_items')
    quantity = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.product_variant.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product_variant}"


class Order(models.Model):
    STATUSES = [
        (0, _("В процессе")),
        (1, _("Доставлено")),
        (3, _("Доставка отменена")),
    ]

    PAYMENT_STATUSES = [
        (0, _("Не оплачено")),
        (1, _("Платеж в процессе")),
        (2, _("Оплачено")),
    ]

    DELIVERY_CHOICES = [
        ('курьером', _("Курьером")),
        ('самовызов', _("Самовывоз")),
    ]

    PAYMENT_METHODS = [
        ('наличкой', _("Наличкой")),
        ('картой', _("Картой")),
    ]

    payment_status = models.IntegerField(choices=PAYMENT_STATUSES, default=1)
    status = models.IntegerField(choices=STATUSES, default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, default=None, blank=True)
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_CHOICES, default='курьером')
    delivery_address = models.CharField(max_length=255, null=True, blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='картой')
    order_number = models.CharField(max_length=20, unique=True, blank=True, null=True)

    def __str__(self):
        return f"Order {self.id} by {self.user}"

    def clean(self):
        if self.delivery_method == 'курьером' and not self.delivery_address:
            raise ValidationError(_('Delivery address is required for courier delivery.'))

    def generate_order_number(self):
        while True:
            order_number = f"#{random.randint(1000000000, 9999999999)}"
            if not Order.objects.filter(order_number=order_number).exists():
                return order_number

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()

        super().save(*args, **kwargs)
        if self.status == 2 and not OrderHistory.objects.filter(order=self).exists():
            OrderHistory.objects.create(user=self.user, order=self)

        if self.status == 2:  # Если статус заказа "Complete"
            with transaction.atomic():  # Обертка для обеспечения атомарности операций
                ordered_items = self.ordered_items.all()  # Получаем все заказанные товары
                for ordered_item in ordered_items:
                    variant = ordered_item.product_variant  # Получаем соответствующий вариант товара
                    variant.stock -= ordered_item.quantity  # Уменьшаем количество товара на складе
                    variant.save()

        def cancel_order(self):
            # Проверяем, можно ли отменить заказ (например, статус должен быть "В процессе")
            if self.status != 0:  # 0 - "В процессе"
                raise ValidationError(_("Order cannot be canceled in its current state."))

            with transaction.atomic():
                # Меняем статус заказа на "Доставка отменена"
                self.status = 2  # 2 - "Доставка отменена"
                self.save()

                for ordered_item in self.ordered_items.all():
                    variant = ordered_item.product_variant
                    variant.stock += ordered_item.quantity
                    variant.save()

            return True
