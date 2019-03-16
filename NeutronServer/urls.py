"""lsoc_updater URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import django.contrib.auth.views
from django.contrib import admin
from django.urls import path

from NeutronServer.forms import BootstrapAuthenticationForm
from update_manager.views import (get_version_control_data, index, users,
                                  version_control, version_control_new, api_version_manifest)

urlpatterns = [
    path('', index, name='index'),
    path('users/', users, name='users'),
    path('versioncontrol/', version_control, name='version_control'),
    path('versioncontrol/new', version_control_new, name='version_control_new'),

    path('versioncontrol/get/all', get_version_control_data, name='get_version_control_data'),

    path('api/versioncontrol', api_version_manifest),

    path('login/',
         django.contrib.auth.views.LoginView.as_view(template_name='auth/login.html',
                                                     authentication_form=BootstrapAuthenticationForm,
                                                     extra_context={
                                                         'title': 'Log in',
                                                     }),
         name='login'),
    path('logout/', django.contrib.auth.views.LogoutView.as_view(next_page='login/'), name='logout'),
    path('admin/', admin.site.urls),
]
