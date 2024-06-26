# Generated by Django 4.2.11 on 2024-06-04 04:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('advertisement', '0007_remove_notification_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='notifications/'),
        ),
    ]
