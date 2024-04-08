# Generated by Django 4.2.11 on 2024-04-05 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0009_mainpageslider_description_mainpageslider_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mainpageslider',
            name='description',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='mainpageslider',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='banners/slider/'),
        ),
        migrations.AlterField(
            model_name='mainpageslider',
            name='title',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Загловок'),
        ),
    ]