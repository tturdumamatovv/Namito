# Generated by Django 4.2.11 on 2024-05-20 05:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0006_brand_categories_alter_image_image_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='keywords',
            field=models.TextField(blank=True, help_text='Запишите ключевые слова через запятую', null=True, verbose_name='Ключевые слова'),
        ),
    ]