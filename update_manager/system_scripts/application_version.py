# Disable annoying 'no member' error
# pylint: disable=E1101
import hashlib

from update_manager.models import NeutronApplication, VersionControl


def clean_string(data):
    return ''.join(e for e in data.lower() if e.isalnum())


def sha256sum(filename):
    h = hashlib.sha256()
    b = bytearray(128*1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        for n in iter(lambda: f.readinto(mv), 0):
            h.update(mv[:n])
    return h.hexdigest()


def install_new_version(form_data, update_package):
    version_control_table = list(VersionControl.objects.values())
    # print(version_control_table)

    # This is safe because we validated this as a number before
    application_id = int(form_data['application'])
    component_name = clean_string(form_data['component'])
    branch = clean_string(form_data['branch'])
    try:
        proposed_version = str(form_data['version_number'])
    except:
        return {'result': False, 'msg': 'Invalid version number.'}

    for application in version_control_table:
        if application['application_id'] == application_id:
            #print("Found app")
            if branch in application['versions']:
                #print("Found branch")
                if component_name in application['versions'][branch]:
                    #print("Found component")

                    proposed_version = proposed_version.split('.')
                    if len(proposed_version) != 3:
                        return {'result': False, 'msg': 'Invalid version number.'}
                    try:
                        major_v_num_p = int(proposed_version[0])
                        minor_v_num_p = int(proposed_version[1])
                        patch_v_num_p = int(proposed_version[2])
                    except:
                        return {'result': False, 'msg': 'Invalid version number.'}

                    # If the version array is empty, we use the start version of '0.0.0' to compare against
                    try:
                        current_version = application['versions'][branch][component_name][-1]['version'].split(
                            '.')
                    except:
                        current_version = '0.0.0'.split('.')

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

                    #print("Current version: " + application['versions'][component_name][branch]['version'])
                    #print("Proposed version: " + form_data["version_number"])

                    application_name = clean_string(
                        str(NeutronApplication.objects.get(pk=application_id)))

                    # Version number is valid, save the file to the correct location
                    save_path = 'update_packages/'+application_name+'/'+branch+ \
                        '/'+component_name+'/' + form_data["version_number"]
                    try:
                        with open(save_path + '.zip', 'wb+') as destination:
                            for chunk in update_package.chunks():
                                destination.write(chunk)
                    except:
                        return {'result': False, 'msg': 'Server error: Could not save update package.'}

                    # Create a changelog for this version
                    # Name: ex. 1.2.0_changelog.txt
                    # Save to same folder as the update package
                    try:
                        with open(save_path + '_changelog.txt', 'w+') as destination:
                            destination.write(form_data["changelog"])
                    except:
                        return {'result': False, 'msg': 'Server error: Could not save update package changelog.'}

                    new_version = {
                        'version': form_data["version_number"],
                        'checksum': sha256sum(save_path+'.zip'),
                        'chainlink': False
                    }

                    # Then update the version number in the database
                    application['versions'][branch][component_name].append(new_version)

                    version_control = VersionControl.objects.get(application_id=application_id)
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
