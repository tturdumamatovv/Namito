# Generated by Django 4.2.11 on 2024-05-22 06:58

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0009_productview'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2024, 5, 22, 6, 58, 47, 257950, tzinfo=datetime.timezone.utc)),
            preserve_default=False,
        ),
    ]
