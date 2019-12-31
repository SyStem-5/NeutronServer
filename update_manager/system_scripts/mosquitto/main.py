# Disable annoying 'no member' error
# pylint: disable=E1101

import base64
import hashlib
import os
import string
from random import choice

from update_manager.models import MQTTACL, MQTTUsers

pbkdf2_iterations = 100000
digest_alg = 'sha256'

generated_password_len = 15


def generate_random(length: int = generated_password_len) -> str:
    return ''.join([choice(string.ascii_letters + string.digits + '_') for i in range(length)])


def clean_string(string: str):
    '''
    The returned string will contain only alpha-numeric characters including '_'
    '''
    return ''.join(e for e in string if e.isalnum() or e == '_')


def generate_hash(password: str, salt: str = "") -> str:
    if salt == "":
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


def add_user(username: str = "", password: str = "", isSuperuser: bool = False) -> (str, str):
    """Returns the username and password used, respectively."""

    if not isinstance(isSuperuser, int):
        return

    if len(username) == 0:
        username = generate_random(10)

    if len(password) == 0:
        password = generate_random()

    complete_hash = generate_hash(password)

    clean_username = clean_string(username)

    MQTTUsers.objects.create(
        username=clean_username,
        password=complete_hash,
        superuser=1 if isSuperuser else 0
    ).save()

    return (username, password)


def remove_user(username: str):
    MQTTUsers.objects.filter(username=username).delete()


def add_acl(username: str, topic: str, permissions: int = 5):
    '''
    Permissions:
        1 -> read-only
        2 -> write-only
        3 -> read/write
    '''
    pass


def remove_acl(username: str):
    pass
