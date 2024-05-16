# Generated by Django 4.2.11 on 2024-05-15 06:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('catalog', '0005_alter_brand_options_alter_category_options_and_more'),
        ('orders', '0003_alter_ordereditem_product_variant'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cart',
            options={'verbose_name': 'Корзина', 'verbose_name_plural': 'Корзины'},
        ),
        migrations.AlterModelOptions(
            name='cartitem',
            options={'verbose_name': 'Пердмет в корзине', 'verbose_name_plural': 'Предметы в корзинах'},
        ),
        migrations.AlterModelOptions(
            name='order',
            options={'verbose_name': 'Заказ', 'verbose_name_plural': 'Заказы'},
        ),
        migrations.AlterModelOptions(
            name='ordereditem',
            options={'verbose_name': 'Предмет в заказе', 'verbose_name_plural': 'Предметы в заказах'},
        ),
        migrations.AlterModelOptions(
            name='orderhistory',
            options={'verbose_name': 'История отзывов', 'verbose_name_plural': 'История отзывов'},
        ),
        migrations.AlterField(
            model_name='cartitem',
            name='cart',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='orders.cart', verbose_name='Корзина'),
        ),
        migrations.AlterField(
            model_name='cartitem',
            name='order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='items', to='orders.order', verbose_name='Заказ'),
        ),
        migrations.AlterField(
            model_name='cartitem',
            name='product_variant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart_items', to='catalog.variant', verbose_name='Варинат'),
        ),
        migrations.AlterField(
            model_name='cartitem',
            name='quantity',
            field=models.PositiveIntegerField(default=1, verbose_name='Количество'),
        ),
        migrations.AlterField(
            model_name='cartitem',
            name='to_purchase',
            field=models.BooleanField(default=True, verbose_name='К покупке'),
        ),
        migrations.AlterField(
            model_name='order',
            name='cart',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='orders.cart', verbose_name='Корзина'),
        ),
        migrations.AlterField(
            model_name='order',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Время создания'),
        ),
        migrations.AlterField(
            model_name='order',
            name='delivery_method',
            field=models.CharField(choices=[('курьером', 'Курьером'), ('самовывоз', 'Самовывоз')], default='курьером', max_length=20, verbose_name='Способ доставки'),
        ),
        migrations.AlterField(
            model_name='order',
            name='finished_at',
            field=models.DateTimeField(blank=True, default=None, null=True, verbose_name='Время окончания'),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_number',
            field=models.CharField(blank=True, max_length=20, null=True, unique=True, verbose_name='Номер заказа'),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('наличкой', 'Наличкой'), ('картой', 'Картой')], default='картой', max_length=20, verbose_name='Способ оплаты'),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment_status',
            field=models.IntegerField(choices=[(0, 'Не оплачено'), (1, 'Платеж в процессе'), (2, 'Оплачено')], default=1, verbose_name='Статус оплаты'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.IntegerField(choices=[(0, 'В процессе'), (1, 'Доставлено'), (2, 'Доставка отменена')], default=0, verbose_name='Статус заказа'),
        ),
        migrations.AlterField(
            model_name='order',
            name='total_amount',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Общая стоимость'),
        ),
        migrations.AlterField(
            model_name='order',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to=settings.AUTH_USER_MODEL, verbose_name='Покупатель'),
        ),
        migrations.AlterField(
            model_name='order',
            name='user_address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='users.useraddress', verbose_name='Адрес покупателя'),
        ),
        migrations.AlterField(
            model_name='ordereditem',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ordered_items', to='orders.order', verbose_name='Заказ'),
        ),
        migrations.AlterField(
            model_name='ordereditem',
            name='product_variant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ordered_items', to='catalog.variant', verbose_name='Вариант'),
        ),
        migrations.AlterField(
            model_name='ordereditem',
            name='quantity',
            field=models.PositiveIntegerField(default=1, verbose_name='Количество'),
        ),
        migrations.AlterField(
            model_name='orderhistory',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_history', to='orders.order', verbose_name='Заказ'),
        ),
        migrations.AlterField(
            model_name='orderhistory',
            name='order_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Время заказа'),
        ),
        migrations.AlterField(
            model_name='orderhistory',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_history', to=settings.AUTH_USER_MODEL, verbose_name='Покупатель'),
        ),
    ]