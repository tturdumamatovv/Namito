# Generated by Django 4.2.11 on 2024-06-03 08:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('advertisement', '0006_notification_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='user',
        ),
    ]
