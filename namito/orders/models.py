import random

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.core.exceptions import ValidationError

from namito.catalog.models import Variant
from namito.users.models import User, UserAddress


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Корзина")
        verbose_name_plural = _("Корзины")

    def __str__(self):
        return f"Корзина {self.user}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name=_('Корзина'))
    product_variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name='cart_items', verbose_name=_('Варинат'))
    quantity = models.PositiveIntegerField(default=1, verbose_name=_('Количество'))
    to_purchase = models.BooleanField(default=True, verbose_name=_('К покупке'))
    order = models.ForeignKey('Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='items', verbose_name=_('Заказ'))

    class Meta:
        verbose_name = _("Пердмет в корзине")
        verbose_name_plural = _("Предметы в корзинах")

    def subtotal(self):
        return self.product_variant.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product_variant}"


class OrderHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='order_history', verbose_name=_('Покупатель'))
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='order_history', verbose_name=_('Заказ'))
    order_date = models.DateTimeField(auto_now_add=True, verbose_name=_('Время заказа'))

    class Meta:
        verbose_name = _("История отзывов")
        verbose_name_plural = _("История отзывов")

    def __str__(self):
        return f"Order history for {self.user} on {self.order_date}"


class OrderedItem(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='ordered_items', verbose_name=_('Заказ'))
    product_variant = models.ForeignKey(Variant, on_delete=models.PROTECT, related_name='ordered_items', verbose_name=_('Вариант'))
    quantity = models.PositiveIntegerField(default=1, verbose_name=_('Количество'))

    class Meta:
        verbose_name = _("Предмет в заказе")
        verbose_name_plural = _("Предметы в заказах")

    def subtotal(self):
        return self.product_variant.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product_variant}"


class Order(models.Model):
    STATUSES = [
        (0, _("В процессе")),
        (1, _("Доставлено")),
        (2, _("Доставка отменена")),
        (3, _("Новый")),
        (4, _("Отправлено"))
    ]

    PAYMENT_STATUSES = [
        (0, _("Не оплачено")),
        (1, _("Платеж в процессе")),
        (2, _("Оплачено")),
    ]

    DELIVERY_CHOICES = [
        ('курьером', _("Курьером")),
        ('самовывоз', _("Самовывоз")),
    ]

    PAYMENT_METHODS = [
        ('наличкой', _("Наличкой")),
        ('картой', _("Картой")),
    ]

    payment_status = models.IntegerField(choices=PAYMENT_STATUSES, default=1, verbose_name=_('Статус оплаты'))
    status = models.IntegerField(choices=STATUSES, default=0, verbose_name=_('Статус заказа'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name=_('Покупатель'))
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders', verbose_name=_('Корзина'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Общая стоимость'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Время создания'))
    finished_at = models.DateTimeField(null=True, default=None, blank=True, verbose_name=_('Время окончания'))
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_CHOICES, default='курьером', verbose_name=_('Способ доставки'))
    user_address = models.ForeignKey(UserAddress, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='orders', verbose_name=_('Адрес покупателя'))
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='картой', verbose_name=_('Способ оплаты'))
    order_number = models.CharField(max_length=20, unique=True, blank=True, null=True, verbose_name=_('Номер заказа'))

    class Meta:
        verbose_name = _("Заказ")
        verbose_name_plural = _("Заказы")

    def __str__(self):
        return f"Order {self.id} by {self.user}"

    def clean(self):
        if self.delivery_method == 'курьером' and not self.user_address:
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

        if self.status == 1:  # Если статус заказа "Complete"
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
