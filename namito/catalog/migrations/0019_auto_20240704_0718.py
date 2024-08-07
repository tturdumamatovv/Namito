# Generated by Django 4.2.11 on 2024-07-04 07:18

from django.db import migrations, models


def set_default_stock(apps, schema_editor):
    Variant = apps.get_model('catalog', 'Variant')
    Variant.objects.filter(stock__isnull=True).update(stock=0)


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0018_variant_catalog_var_price_9d57b4_idx_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='variant',
            name='stock',
            field=models.PositiveIntegerField(default=0, verbose_name='Количество'),
        ),
        migrations.RunPython(set_default_stock),
    ]
