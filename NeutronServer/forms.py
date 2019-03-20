from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy

from NeutronServer.field_validators import validate_file_field
from NeutronServer.fields import (ChoiceFieldIntegerNoValidation,
                                  ChoiceFieldTextNoValidation)


class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""

    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'User name'}))

    password = forms.CharField(label=ugettext_lazy("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder': 'Password'}))

class PublishNewVersionForm(forms.Form):
    application = ChoiceFieldIntegerNoValidation(widget=forms.Select({
        'name': 'application',
        'id': 'inputApp',
        'class': 'form-control',
        'required': ''}))
    branch = ChoiceFieldTextNoValidation(widget=forms.Select({
        'name': 'branch',
        'id': 'inputAppBranch',
        'class': 'form-control',
        'required': ''}))
    component = ChoiceFieldTextNoValidation(widget=forms.Select({
        'name': 'component',
        'id': 'inputAppComponent',
        'class': 'form-control',
        'required': ''}))
    version_number = forms.CharField(max_length=8,
                                     min_length=5,
                                     widget=forms.TextInput({
                                         'name': 'version_number',
                                         'id': 'inputVersionNumber',
                                         'class': 'form-control',
                                         'autocomplete': 'on',
                                         'data-mask': '99.99.99',
                                         'placeholder': '[MAJOR].[MINOR].[PATCH]',
                                         'required': ''}))
    changelog = forms.CharField(min_length=5,
                                widget=forms.Textarea({
                                    'name': 'changelog',
                                    'id': 'inputChangelog',
                                    'class': 'form-control',
                                    'required': ''
                                }))
    update_package = forms.FileField(validators=[validate_file_field],
        widget=forms.FileInput({
        'name': 'update_package',
        'id': 'inputUpdatePackage',
        'class': 'form-control',
        'style': 'height: 0%;',
        'accept': '.zip',
        'required': ''}))

    is_push_update = forms.BooleanField(required=False,
                                        widget=forms.CheckboxInput({
                                            'name': 'is_push_update',
                                            'id': 'inputIsPushUpdate',
                                            'type': 'checkbox'
                                        }))
    is_chainlink = forms.BooleanField(required=False,
                                        widget=forms.CheckboxInput({
                                            'name': 'is_chainlink',
                                            'id': 'inputIsChainLink',
                                            'type': 'checkbox'
                                        }))
