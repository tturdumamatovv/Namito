# Generated by Django 4.2.11 on 2024-07-04 05:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0017_variant_discounted_price'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='variant',
            index=models.Index(fields=['price'], name='catalog_var_price_9d57b4_idx'),
        ),
        migrations.AddIndex(
            model_name='variant',
            index=models.Index(fields=['discounted_price'], name='catalog_var_discoun_c5b4b0_idx'),
        ),
    ]