# Generated by Django 2.2 on 2021-09-06 19:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comic_app', '0006_auto_20210905_2343'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comic',
            name='created_at',
            field=models.DateField(auto_now_add=True),
        ),
    ]
