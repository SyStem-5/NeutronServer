# Disable annoying 'no member' error
# pylint: disable=E1101

import json

from django.core.exceptions import ObjectDoesNotExist

from update_manager.models import User, UpdaterList
from update_manager.system_scripts.mosquitto.main import add_user as mqtt_add_user


def generate_updater(username: str, data: dict) -> (bool, str, str, str):
    """Returns a touple (result, identifier, passkey)"""

    # Stored in the db
    """
    {
        "updaters": {
            "testuser_mqtt": {
                "LSOC": {
                    "stable": ["NeutronCommunicator", "BlackBox", "WebInterface"]
                }
            }
        }
    }
    """
    # Received from web
    """
    "LSOC": {
        "stable": ["NeutronCommunicator", "BlackBox", "WebInterface"],
        "beta": ["NeutronCommunicator", "BlackBox", "WebInterface"]
    }
    """

    # Get the user PK by username
    try:
        user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        return (False, "User not found", "", "")

    # Call mqtt_add_user
    identifier, passkey = mqtt_add_user()

    # Generate an updaterlist with that user
    if user.updaterlist.updaters == {}:
        updaters_list = {"updaters": {}}
        updaters_list["updaters"][identifier] = data
    elif "updaters" in user.updaterlist.updaters:
        updaters_list = user.updaterlist.updaters
        updaters_list["updaters"][identifier] = data

    try:
        # Append or edit the already existing user updater list
        UpdaterList.objects.filter(user = user).update(
            updaters = updaters_list
        )
    except ObjectDoesNotExist:
        return (False, "Could not find the UpdaterList entry for this user. Manual action is required.", "", "")

    return (True, "", identifier, passkey)


def remove_updater(username: str, identifier: str) -> (bool, str):
    return (False, "UNIMPLEMENTED")
