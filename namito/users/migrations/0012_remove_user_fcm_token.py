# Generated by Django 4.2.11 on 2024-06-07 10:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_remove_user_fcm_token'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='fcm_token',
        ),
    ]
