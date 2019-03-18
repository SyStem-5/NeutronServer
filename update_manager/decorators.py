# Disable annoying 'no member' error
# pylint: disable=E1101

import base64
from functools import wraps

from django.http import JsonResponse

from update_manager.models import MQTTUsers
from update_manager.mosquitto.main import generate_hash


def mqtt_auth(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        req = request.GET

        received_fields = list(req)
        required_fields = ['username', 'password']

        for field in required_fields:
            if field not in received_fields:
                return JsonResponse({'message': 'Error: missing field/s.', 'code': 400})

        clean_username = ''.join(e for e in req['username'].lower() if e.isalnum())

        try:
            user = MQTTUsers.objects.get(username=clean_username)
        except:
            return JsonResponse({'message': 'Error: Authentication failed.', 'code': 403})

        proposed_user_salt = base64.b64decode(
            user.password.split('$')[3].encode('utf-8'))

        if generate_hash(req['password'], proposed_user_salt) != user.password:
            return JsonResponse({'message': 'Error: Authentication failed.', 'code': 403})

        # print('-'*5+'MQTT'+'-'*5)
        # print('User authenticated.')
        # print('-'*14)

        return function(request, *args, **kwargs)

    return wrap
