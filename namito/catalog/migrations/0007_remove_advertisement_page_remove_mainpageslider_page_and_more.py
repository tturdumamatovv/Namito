# Generated by Django 4.2.11 on 2024-04-29 05:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0006_alter_variant_color_remove_variant_size_variant_size'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='advertisement',
            name='page',
        ),
        migrations.RemoveField(
            model_name='mainpageslider',
            name='page',
        ),
        migrations.DeleteModel(
            name='StaticPage',
        ),
        migrations.DeleteModel(
            name='Advertisement',
        ),
        migrations.DeleteModel(
            name='MainPage',
        ),
        migrations.DeleteModel(
            name='MainPageSlider',
        ),
    ]