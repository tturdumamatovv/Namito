# Generated by Django 4.2.11 on 2024-05-28 08:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0006_paymentmethod'),
    ]

    operations = [
        migrations.CreateModel(
            name='FAQ',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(blank=True, max_length=255, null=True, verbose_name='Вопросы')),
                ('question_en', models.CharField(blank=True, max_length=255, null=True, verbose_name='Вопросы')),
                ('question_ru', models.CharField(blank=True, max_length=255, null=True, verbose_name='Вопросы')),
                ('answer', models.CharField(blank=True, max_length=255, null=True, verbose_name='Ответы')),
                ('answer_en', models.CharField(blank=True, max_length=255, null=True, verbose_name='Ответы')),
                ('answer_ru', models.CharField(blank=True, max_length=255, null=True, verbose_name='Ответы')),
                ('static_page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pages.staticpage')),
            ],
        ),
    ]
