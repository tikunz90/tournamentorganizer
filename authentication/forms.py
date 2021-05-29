# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from beachhandball_app.models.Tournament import Tournament
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder" : "Username",                
                "class": "form-control"
            }
        ))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder" : "Password",                
                "class": "form-control"
            }
        ))

class SelectTournamentForm(forms.Form):
    class Meta:
        fields = ('tournaments',)
        widgets = {
            'tournaments': forms.widgets.Select(attrs={'class': "form-control selectpicker", 'data-style':"btn btn-info btn-round"}),
        }

    def __init__(self, *args, **kwargs):
        self.gbo_organizer = kwargs.pop('gbo_organizer')
        super().__init__(*args, **kwargs)
        

        MYQUERY = Tournament.objects.filter(organizer=self.gbo_organizer).values_list('id', 'name')
        self.fields['tournaments'] = forms.ChoiceField(choices=(*MYQUERY,))


class SignUpForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder" : "Username",                
                "class": "form-control"
            }
        ))
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder" : "Email",                
                "class": "form-control"
            }
        ))
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder" : "Password",                
                "class": "form-control"
            }
        ))
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder" : "Password check",                
                "class": "form-control"
            }
        ))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
