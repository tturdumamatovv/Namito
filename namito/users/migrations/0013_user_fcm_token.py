# Generated by Django 4.2.11 on 2024-06-07 10:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_remove_user_fcm_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='fcm_token',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Токен'),
        ),
    ]
