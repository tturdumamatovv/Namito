# Generated by Django 4.2.11 on 2024-04-05 08:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0006_alter_advertisement_button_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='mainpage',
            name='banner1_link',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mainpage',
            name='banner2_link',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mainpage',
            name='banner3_link',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='MainPageSlider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='banners/slider/')),
                ('link', models.URLField(blank=True, null=True)),
                ('page', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='catalog.mainpage')),
            ],
        ),
    ]