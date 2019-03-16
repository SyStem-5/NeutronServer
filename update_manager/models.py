# Disable 'no member' error
# pylint: disable=E1101
# Disable 'unsubscriptable' object
# pylint: disable=E1136

import datetime

from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from update_manager.system_scripts.application_utils import (cleanup_application_postdelete,
                                                             setup_new_application)


class UpdaterList(models.Model):
    class Meta:
        verbose_name = 'user updater'
        verbose_name_plural = 'User updaters'
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    updaters = JSONField(default=dict)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_updater_list(sender, instance, created, **kwargs):
    UpdaterList.objects.get_or_create(user=instance)

# @receiver(post_save, sender=User)
# def save_updater_list(sender, instance, **kwargs):
#     instance.updaterlist.save()


###########################################################################################


def default_branches():
    return {'branches': ['stable', 'beta', 'alpha']}


def blank_components():
    return {'components': []}


class NeutronApplication(models.Model):
    class Meta:
        verbose_name = 'application'
        verbose_name_plural = 'Applications'

    name = models.TextField(max_length=50, unique=True, blank=False)

    branches = JSONField(default=default_branches)

    components = JSONField(default=blank_components)

    def get_components_clean(self):
        '''
        Returns a component list of an application totally clean. No whitespace or special characters.
        '''
        component_list = []
        for component in self.components['components']:
            component_list.append(
                ''.join(e for e in component.lower() if e.isalnum()))
        return component_list

    def get_branches_clean(self):
        '''
        Returns a branch list of an application totally clean. No whitespace or special characters.
        '''
        branch_list = []
        for branch in self.branches['branches']:
            branch_list.append(
                ''.join(e for e in branch.lower() if e.isalnum()))
        return branch_list

    def get_name_clean(self):
        '''
        Returns alpha-numeric application name with no whitespace.
        '''
        return ''.join(e for e in self.name.lower() if e.isalnum())
    
    def __str__(self):
        return self.name


@receiver(post_save, sender=NeutronApplication)
def create_application_setup(sender, instance, **kwargs):
    setup_new_application(
        instance.get_name_clean(), 
        instance.get_branches_clean(), 
        instance.get_components_clean()
    )

    versions_field = {}
    for component in instance.get_components_clean():
        versions_field[component] = {}

        for branch in instance.get_branches_clean():
            versions_field[component][branch] = {"version":"0.0.0", "checksum":""}

    VersionControl.objects.get_or_create(application=instance, versions=versions_field)


@receiver(post_delete, sender=NeutronApplication)
def delete_application(sender, instance, **kwargs):
    cleanup_application_postdelete(instance.get_name_clean())


###########################################################################################


class VersionControl(models.Model):
    class Meta:
        verbose_name = 'application version'
        verbose_name_plural = 'Application versions'

    application = models.OneToOneField(NeutronApplication, on_delete=models.CASCADE)
    versions = JSONField(default=dict)
    last_updated = models.DateTimeField(auto_now=True)

@receiver(post_save, sender=VersionControl)
def save_version_control(sender, instance, **kwargs):
    instance.last_updated = datetime.datetime.now()


###########################################################################################

class MQTTUsers(models.Model):
    class Meta:
        verbose_name = 'mqtt user'
        verbose_name_plural = 'MQTT Users'

    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150)
    password = models.CharField(max_length=500)
    superuser = models.IntegerField(null=False, default=0)

class MQTTACL(models.Model):
    class Meta:
        verbose_name = 'mqtt access control'
        verbose_name_plural = 'MQTT ACLs'

    username = models.CharField(max_length=150)
    topic = models.CharField(max_length=100)

    # 2 write, 5 read, 7 read/write
    rw = models.IntegerField(null=False, default=5)