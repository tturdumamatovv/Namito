# Generated by Django 4.2.11 on 2024-04-30 05:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_useraddress_street_alter_useraddress_city'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraddress',
            name='is_primary',
            field=models.BooleanField(default=False),
        ),
    ]