# Generated by Django 2.2 on 2021-09-01 23:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comic_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='comic',
            name='notes',
            field=models.CharField(default='enter notes here', max_length=255),
        ),
    ]
