# Generated by Django 2.1.7 on 2019-03-12 20:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('update_manager', '0015_auto_20190312_2046'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mqttusers',
            name='id',
            field=models.IntegerField(auto_created=True, primary_key=True, serialize=False),
        ),
    ]
