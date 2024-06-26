# Generated by Django 4.2.11 on 2024-05-27 05:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_status',
            field=models.IntegerField(choices=[(0, 'Не оплачено'), (2, 'Оплачено')], default=0, verbose_name='Статус оплаты'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.IntegerField(choices=[(0, 'В процессе'), (1, 'Доставлено'), (2, 'Отменен'), (3, 'Отправлено')], default=0, verbose_name='Статус заказа'),
        ),
    ]
