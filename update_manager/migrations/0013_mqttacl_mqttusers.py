# Generated by Django 2.1.7 on 2019-03-11 10:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('update_manager', '0012_remove_versioncontrol_changelog'),
    ]

    operations = [
        migrations.CreateModel(
            name='MQTTACL',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=150)),
                ('topic', models.CharField(max_length=100)),
                ('rw', models.IntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='MQTTUsers',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=150)),
                ('password', models.CharField(max_length=500)),
                ('superuser', models.IntegerField(default=0)),
            ],
        ),
    ]
