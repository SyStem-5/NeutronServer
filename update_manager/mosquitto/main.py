# Disable annoying 'no member' error
# pylint: disable=E1101

import base64
import hashlib
import os

from update_manager.models import MQTTACL, MQTTUsers

pbkdf2_iterations = 100000
digest_alg = 'sha256'


def generate_hash(password, salt=''):

    if not salt:
        salt = base64.b64encode(os.urandom(20))
    else:
        salt = base64.b64encode(salt)

    pbkdf2_hash = hashlib.pbkdf2_hmac(
        digest_alg,
        str.encode(password),
        salt,
        pbkdf2_iterations
    )

    complete_hash = 'PBKDF2${}${}${}${}'.format(
        digest_alg,
        pbkdf2_iterations,
        salt.decode("utf-8"),
        base64.b64encode(pbkdf2_hash).decode("utf-8")
    )
    return complete_hash


def add_user(username, password, isSuperuser=0):

    if not isinstance(isSuperuser, int):
        return

    complete_hash = generate_hash(password)

    clean_username = ''.join(e for e in username.lower() if e.isalnum())

    MQTTUsers.objects.create(
        username=clean_username,
        password=complete_hash,
        superuser=isSuperuser
    ).save()


def remove_user(username):
    MQTTUsers.objects.filter(username=username).delete()


def add_acl(username, topic, permissions=5):
    '''
    Permissions: 2 - write, 5 - read, 7 - read/write
    '''
    pass


def remove_acl(username):
    pass
