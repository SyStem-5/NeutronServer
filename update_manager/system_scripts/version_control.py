# Disable annoying 'no member' error
# pylint: disable=E1101
import hashlib
from os import mkdir
from shutil import rmtree
from zipfile import ZIP_DEFLATED, ZipFile

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from NeutronServer.settings import VERSION_CONTROL_ROOT
from update_manager.models import (NeutronApplication, UpdaterList,
                                   VersionControl)


def clean_string(data):
    return ''.join(e for e in data if e.isalnum())


def sha256sum(filename):
    h = hashlib.sha256()
    b = bytearray(128*1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        for n in iter(lambda: f.readinto(mv), 0):
            h.update(mv[:n])
    return h.hexdigest()


def validate_version(current_version, proposed_version):
    proposed_version = proposed_version.split('.')

    if len(proposed_version) != 3:
        return {'result': False, 'msg': 'Invalid version number.'}
    try:
        major_v_num_p = int(proposed_version[0])
        minor_v_num_p = int(proposed_version[1])
        patch_v_num_p = int(proposed_version[2])
    except:
        return {'result': False, 'msg': 'Invalid version number.'}

    current_version = current_version.split('.')

    try:
        major_v_num_c = int(current_version[0])
        minor_v_num_c = int(current_version[1])
        patch_v_num_c = int(current_version[2])
    except:
        return {'result': False, 'msg': 'Server error: Saved version number is invalid.'}

    if major_v_num_p > major_v_num_c:
        # Continue with file save
        pass
    elif major_v_num_p == major_v_num_c:
        if minor_v_num_p > minor_v_num_c:
            # Continue with file save
            pass
        elif minor_v_num_p == minor_v_num_c:
            if patch_v_num_p > patch_v_num_c:
                # Continue with file save
                pass
            else:
                # No need for the same/lower version to be uploaded
                return {'result': False, 'msg': 'Version number has to be an increase from the current one.'}
        else:
            return {'result': False, 'msg': 'Version number has to be an increase from the current one.'}
    else:
        return {'result': False, 'msg': 'Version number has to be an increase from the current one.'}
    
    return {'result': True}


def install_new_version(form_data, update_package):
    version_control_table = list(VersionControl.objects.values())
    # print(version_control_table)

    # This is safe because we validated this as a number before
    application_id = int(form_data["application"])
    component_name = clean_string(form_data["component"])
    branch = clean_string(form_data["branch"])
    try:
        proposed_version = str(form_data["version_number"])
    except:
        return {'result': False, 'msg': 'Invalid version number.'}

    for application in version_control_table:
        if application["application_id"] == application_id:
            #print("Found app")
            if branch in application["versions"]:
                #print("Found branch")
                if component_name in application["versions"][branch]:
                    #print("Found component")

                    # If the version array is empty, we use the start version of '0.0.0' to compare against
                    try:
                         current_version = application["versions"][branch][component_name][-1]["version"]
                    except:
                         current_version = '0.0.0'

                    version_validator = validate_version(
                        current_version=current_version, 
                        proposed_version=proposed_version)

                    if version_validator['result'] == False:
                        return version_validator

                    #print("Current version: " + application['versions'][component_name][branch]['version'])
                    #print("Proposed version: " + form_data["version_number"])

                    application_name = str(NeutronApplication.objects.get(pk=application_id))

                    # Version number is valid, save the file to the correct location
                    # Name: ex. 1.2.0_changelog.txt
                    # Save to same folder as the update package
                    save_path = VERSION_CONTROL_ROOT+'/'+application_name+'/'+branch + \
                        '/'+component_name+'/' + proposed_version

                    version_control = {}

                    # Try to get the application version control from the database
                    try:
                        version_control = VersionControl.objects.get(application_id=application_id)
                    except (ObjectDoesNotExist):
                        return {'result': False, 'msg': 'Server error: Could not find version control data for the selected app.'}
                    else:
                        # If we get the version control, try to save the changelog
                        try:
                            with open(save_path + '_changelog.txt', 'w+') as destination:
                                destination.write(form_data["changelog"])
                        except:
                            return {'result': False, 'msg': 'Server error: Could not save update changelog.'}
                        else:
                            # We saved the changelog, save the update package
                            try:
                                temp_loc=VERSION_CONTROL_ROOT+'/'+proposed_version+'-temp/'
                                mkdir(path=temp_loc)
                                with ZipFile(save_path + '.zip', 'w', compression=ZIP_DEFLATED) as zipfile:
                                    with open(temp_loc + str(update_package), 'wb+') as destination2:
                                        for chunk2 in update_package.chunks():
                                            destination2.write(chunk2)
                                    #zipfile.writestr(zinfo_or_arcname=save_path + '.zip', data=destination2)
                                    zipfile.write(temp_loc + str(update_package), arcname=str(update_package))
                            except FileExistsError:
                                return {'result': False, 'msg': 'Server error: Temporary folder already exists. Try again.'}
                            except FileNotFoundError:
                                return {'result': False, 'msg': 'Server error: Temporary folder not found.'}
                            finally:
                                # Just so we don't trash the log with useless info
                                try:
                                    rmtree(temp_loc)
                                except:
                                    print("Could not clean-up update publish temporary folder.")
                                

                    # The file saving was successful
                    # Generate the hash and save it to the database
                    new_version = {
                        'version': proposed_version,
                        'checksum': sha256sum(save_path+'.zip'),
                        'chainlink': form_data["is_chainlink"]
                    }
                    # Then update the version number in the database
                    application['versions'][branch][component_name].append(
                        new_version)

                    version_control.versions = application['versions']
                    version_control.save()

                    return {'result': True, 'msg': 'New version successfuly published.'}
                else:
                    #print("Branch not found")
                    return {'result': False, 'msg': 'Component does not exist.'}
            else:
                #print("Component not found")
                return {'result': False, 'msg': 'Branch does not exist.'}

    return {'result': False, 'msg': 'Could not find the application specified.'}


def generate_update_manifest(request):
    try:
        neutron_user = clean_string(request["neutronuser"])
        updater_username = request["username"]
        asked_application = clean_string(request["application"])
        asked_branch = request["branch"]
        asked_components = request["components"].split(',')
        asked_versions = request["versions"].split(',')
    except (KeyError):
        return {'result': False, 'msg': 'Unknown parameter.'}

    if len(asked_components) != len(asked_versions):
        return {'result': False, 'msg': 'Components & versions parameter length not matching.'}

    try:
        user = UpdaterList.objects.get(user=User.objects.get(username=neutron_user))
    except (ObjectDoesNotExist):
        return {'result': False, 'msg': 'Unknown user.'}

    #print(user.updaters)

    allowed_components = []
    component_versions = []

    # Check if the updater list is empty, if it is, return error
    if user.updaters:
        #print("found updater list")
        if updater_username in user.updaters["updaters"]:
            print("Updater is valid")

            if asked_application in user.updaters["updaters"][updater_username]:
                print("Application access granted")

                if asked_branch in user.updaters["updaters"][updater_username][asked_application]:
                    print("Branch access granted")

                    # The updater has access to the application/branch, now we determine which updater is allowed and add them to the list
                    for component in asked_components:
                        if component in user.updaters["updaters"][updater_username][asked_application][asked_branch]:
                            allowed_components.append(component)
                            component_versions.append(asked_versions[asked_components.index(component)])

                else:
                    return {'result': False, 'msg': 'Branch access denied.'}
            else:
                return {'result': False, 'msg': 'Application access denied.'}
        else:
            return {'result': False, 'msg': 'Updater does not belong to the provided user.'}
    else:
        return {'result': False, 'msg': 'Updater does not belong to the provided user.'}

    #print(allowed_components)
    #print(component_versions)
    #print(asked_components)
    #print(asked_versions)

    try:
        version_control = VersionControl.objects.get(application=NeutronApplication.objects.get(name=asked_application))
    except (ObjectDoesNotExist):
        return {'result': False, 'msg': 'Unknown application.'}

    manifest = {"manifest": {}}

    for component in allowed_components:
        try:
            for version in version_control.versions[asked_branch][component]:
                #pass
                validator = validate_version(component_versions[allowed_components.index(component)], version["version"])
                if validator["result"] == True and (version["chainlink"] or version["version"] == version_control.versions[asked_branch][component][-1]["version"]):
                    manifest["manifest"].setdefault(component,[]).append(version)
        except:
            return {'result': False, 'msg': 'Server error: Could not locate version control data.'}
        

    return {'result': True, 'msg': manifest}
