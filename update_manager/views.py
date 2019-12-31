# Disable annoying 'no member' error
# pylint: disable=E1101

import os
import json

from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from django.shortcuts import redirect, render

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from NeutronServer.settings import VERSION_CONTROL_ROOT
from update_manager.models import UpdaterList
from NeutronServer.forms import PublishNewVersionForm, AccoutManagementForm
from update_manager.decorators import mqtt_auth
from update_manager.models import NeutronApplication, VersionControl
from update_manager.system_scripts.updaters import generate_updater
from update_manager.system_scripts.version_control import (generate_update_manifest,
                                                           install_new_version, clean_string)


# @login_required(redirect_field_name='', login_url='login/')
@permission_required('superuser', login_url='login/')
def index(request):
    template = 'index.html'

    return render(request, template)


@permission_required('superuser', login_url='login/')
def users(request):
    template = 'users.html'
    return render(request, template, {
        'users': User.objects.all()
    })


@permission_required('superuser', login_url='login/')
def users_get(request):
    from django.core import serializers
    users = serializers.serialize("json", User.objects.all())

    return JsonResponse({'users': json.loads(users)})


@permission_required('superuser', login_url='login/')
def users_add(request):
    template = 'user_management/new_user.html'

    if request.method == 'GET':
        return render(request, template, {
            'form': AccoutManagementForm
        })
    elif request.method == 'POST':
        form = AccoutManagementForm(request.POST)

        if form.is_valid():
            User.objects.create_user(
                first_name=form.cleaned_data['firstname'],
                last_name=form.cleaned_data['lastname'],
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1'])

            return redirect(to='users')
        else:
            return render(request, template, {
                'form': AccoutManagementForm,
                'errors': form.errors
            })


@permission_required('superuser', login_url='login/')
def users_updaters_get(request):
    from django.core import serializers
    updaters = serializers.serialize("json", UpdaterList.objects.all())

    return JsonResponse({'users': json.loads(updaters)})


@permission_required('superuser', login_url='login/')
def users_updaters_new(request):
    if "data" in request.POST and "username" in request.POST:
        data = request.POST["data"]
        username = request.POST["username"]

        try:
            data = json.loads(data)
            result, msg, identifier, passkey = generate_updater(str(username), data)
            return JsonResponse({'result': result, 'msg': msg, 'username': identifier, 'password': passkey})
        except json.JSONDecodeError:
            return JsonResponse({'result': False, 'msg': 'Invalid data.'})

    else:
        return JsonResponse({'result': False, 'msg': 'Invalid format.'})


@permission_required('superuser', login_url='login/')
def version_control(request):
    #main.add_user('testuser_mqtt', 'stupidpass.exe')
    template = 'version_control/dashboard.html'
    return render(request, template)


@permission_required('superuser', login_url='login/')
def version_control_new(request):
    if request.method == 'GET':
        template = 'version_control/new_version.html'

        return render(request, template, {'form': PublishNewVersionForm()})
    elif request.method == 'POST':
        form = PublishNewVersionForm(request.POST, request.FILES)
        if form.is_valid():
            return JsonResponse(install_new_version(form.cleaned_data, request.FILES))
        else:
            return JsonResponse({'result': False, 'msg': str(form.errors)})


@mqtt_auth
def api_version_manifest(request):
    #print(request.GET)
    return JsonResponse(generate_update_manifest(request.GET))


@permission_required('superuser', login_url='login/')
def get_version_control_data(request):
    vc_data = list(VersionControl.objects.values())

    return JsonResponse({'version_control': vc_data})


@permission_required('superuser', login_url='login/')
def get_version_control_apps(request):
    app_data = list(NeutronApplication.objects.values())

    return JsonResponse({'applications_data': app_data})


# Temporary
@mqtt_auth
def version_control_download(request):
    request = request.GET

    try:
        neutron_user = clean_string(request["neutronuser"])
        updater_username = request["username"]
        asked_application = clean_string(request["application"])
        asked_branch = request["branch"]
        asked_component = request["component"]
        asked_version = request["version"]
    except (KeyError):
        return {'result': False, 'msg': 'Unknown parameter.'}

    try:
        user = UpdaterList.objects.get(user=User.objects.get(username=neutron_user))
    except (ObjectDoesNotExist):
        return {'result': False, 'msg': 'Unknown user.'}

    # Check if the updater list is empty, if it is, return error
    if user.updaters:
        #print("found updater list")
        if updater_username in user.updaters["updaters"]:
            #print("Updater is valid")

            if asked_application in user.updaters["updaters"][updater_username]:
                #print("Application access granted")

                if asked_branch in user.updaters["updaters"][updater_username][asked_application]:
                    #print("Branch access granted")

                    if asked_component in user.updaters["updaters"][updater_username][asked_application][asked_branch]:
                        file_path = VERSION_CONTROL_ROOT+'/{}/{}/{}/{}.zip'.format(asked_application, asked_branch, asked_component, asked_version)
                        #os.path.join(VERSION_CONTROL_ROOT, '/LSOC/stable/BlackBox/0.2.1.zip')

                        #print(VERSION_CONTROL_ROOT+'/LSOC/BlackBox/stable/0.2.1')
                        if os.path.exists(file_path):
                            with open(file_path, 'rb') as fh:
                                response = HttpResponse(fh.read(), content_type="application/octet-stream")
                                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                                return response
                        raise Http404
                    else:
                        return {'result': False, 'msg': 'Component access denied.'}

                else:
                    return {'result': False, 'msg': 'Branch access denied.'}
            else:
                return {'result': False, 'msg': 'Application access denied.'}
        else:
            return {'result': False, 'msg': 'Updater does not belong to the provided user.'}
    else:
        return {'result': False, 'msg': 'Updater does not belong to the provided user.'}
