# Generated by Django 4.2.11 on 2024-06-07 10:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_alter_user_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(blank=True, default=1, max_length=254, verbose_name='Имейл'),
            preserve_default=False,
        ),
    ]