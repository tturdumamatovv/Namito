# Generated by Django 4.2.11 on 2024-06-03 09:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0014_alter_mainpageslider_small_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contacts',
            name='meta_description',
        ),
        migrations.RemoveField(
            model_name='contacts',
            name='meta_image',
        ),
        migrations.RemoveField(
            model_name='contacts',
            name='meta_title',
        ),
        migrations.CreateModel(
            name='MainPageLayoutMeta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meta_title', models.CharField(blank=True, max_length=255, null=True, verbose_name='Мета Заголовок')),
                ('meta_description', models.TextField(blank=True, null=True, verbose_name='Мета Описание')),
                ('meta_image', models.ImageField(blank=True, null=True, upload_to='layout/meta_image', verbose_name='Мета Картинки')),
                ('page', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='pages.mainpage')),
            ],
        ),
    ]
