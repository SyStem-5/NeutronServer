# Generated by Django 2.1.7 on 2019-02-28 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('update_manager', '0009_auto_20190228_1917'),
    ]

    operations = [
        migrations.AddField(
            model_name='versioncontrol',
            name='last_updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
