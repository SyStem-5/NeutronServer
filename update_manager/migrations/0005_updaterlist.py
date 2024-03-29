# Generated by Django 2.1.7 on 2019-02-25 22:44

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('update_manager', '0004_auto_20190225_2223'),
    ]

    operations = [
        migrations.CreateModel(
            name='UpdaterList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updaters', django.contrib.postgres.fields.jsonb.JSONField()),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='updaters', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
