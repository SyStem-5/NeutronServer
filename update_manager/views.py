# Disable annoying 'no member' error
# pylint: disable=E1101

import json

from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from django.shortcuts import redirect, render

from NeutronServer.forms import PublishNewVersionForm
from update_manager.decorators import mqtt_auth
from update_manager.models import NeutronApplication, VersionControl
from update_manager.mosquitto import main
from update_manager.system_scripts.application_version import \
    install_new_version


# @login_required(redirect_field_name='', login_url='login/')
@permission_required('superuser', login_url='login/')
def index(request):
    template = 'index.html'

    # , {'title': 'LSOC - Dashboard', 'blackbox_state': mqtt_connection.blackbox_status}
    return render(request, template)


@permission_required('superuser', login_url='login/')
def users(request):
    template = 'users.html'
    return render(request, template)


@permission_required('superuser', login_url='login/')
def version_control(request):
    #main.add_user('testuser', 'jahahaha')
    template = 'version_control/version_control.html'
    return render(request, template, {'version_control': VersionControl.objects.all()})


@permission_required('superuser', login_url='login/')
def version_control_new(request):
    if request.method == 'GET':
        template = 'version_control/new_version.html'

        return render(request, template, {'form': PublishNewVersionForm(), 'version_control': VersionControl.objects.all()})
    elif request.method == 'POST':
        form = PublishNewVersionForm(request.POST, request.FILES)
        # print(request.FILES)
        if form.is_valid():
            return JsonResponse(install_new_version(form.cleaned_data, request.FILES['update_package']))
        else:
            return JsonResponse({'result': False, 'msg': str(form.errors)})


@mqtt_auth
def api_version_manifest(request):
    print(request.GET)
    return JsonResponse({"message": "Hiii!"})


@permission_required('superuser', login_url='login/')
def get_version_control_data(request):
    vc_data = list(VersionControl.objects.values())
    app_data = list(NeutronApplication.objects.values())

    return JsonResponse({'version_control': vc_data, 'applications_data': app_data})
