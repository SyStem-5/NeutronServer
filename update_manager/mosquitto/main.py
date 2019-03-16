# Disable annoying 'no member' error
# pylint: disable=E1101

from update_manager.models import MQTTACL, MQTTUsers


def add_user(username, password, isSuperuser=0):
    MQTTUsers.objects.create(
        username=username,
        password=password,
        superuser=isSuperuser
    ).save()

    #add_acl(self.username, 'nowhere', 7)


def remove_user(username):
    pass


def add_acl(username, topic, permissions=5):
    '''
    Permissions: 2 - write, 5 - read, 7 - read/write
    '''
    pass


def remove_acl(username):
    pass
