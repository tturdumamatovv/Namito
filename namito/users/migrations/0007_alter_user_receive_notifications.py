# Generated by Django 4.2.11 on 2024-06-03 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_user_receive_notifications'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='receive_notifications',
            field=models.BooleanField(blank=True, null=True, verbose_name='Получать уведомления'),
        ),
    ]
