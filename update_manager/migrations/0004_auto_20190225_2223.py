# Generated by Django 2.1.7 on 2019-02-25 22:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('update_manager', '0003_auto_20190225_2219'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='groups',
        ),
        migrations.RemoveField(
            model_name='user',
            name='user_permissions',
        ),
        migrations.DeleteModel(
            name='User',
        ),
    ]
