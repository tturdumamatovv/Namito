# Generated by Django 4.2.11 on 2024-05-15 04:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0003_product_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='image',
            name='variant',
        ),
        migrations.AddField(
            model_name='image',
            name='color',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='images', to='catalog.color', verbose_name='Цвет'),
        ),
        migrations.AddField(
            model_name='image',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='images', to='catalog.product'),
        ),
    ]
