# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.shortcuts import render
from datetime import datetime

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, Group
from authentication.models import GBOUser
from django.forms.utils import ErrorList
from django.http import HttpResponse
from .forms import LoginForm, SignUpForm
from django.views.generic import TemplateView

from beachhandball_app.services import services as s

def login_view(request):
    form = LoginForm(request.POST or None)

    msg = None

    if request.method == "POST":

        if form.is_valid():
            # get token from gbo
            print()
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            result = s.SWS.create_session(username, password)
            if result['isError'] is not True:
                if User.objects.filter(username=username).count() == 0:
                    user = User.objects.create_user(username, result['message']['user']['email'], password)
                    user.first_name = result['message']['user']['name']
                    user.last_name = result['message']['user']['family_name']
                    user.save()
                    guser = GBOUser(user=user,
                    gbo_user=result['message']['user']['email'],
                    token = result['message']['token'].split(' ')[1],
                    validUntil = datetime.utcfromtimestamp(result['message']['expiresIn'] / 1000))
                    guser.subject_id = s.SWS.getGBOUserId(guser)
                    guser.save()
                    to_group = Group.objects.get(name='tournament_organizer')
                    to_group.user_set.add(user)
                
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    if user.is_superuser is True:
                        if GBOUser.objects.filter(user=user).count() == 0:
                            guser = GBOUser(user=user,
                            gbo_user=result['message']['user']['email'],
                            token = result['message']['token'].split(' ')[1],
                            validUntil = datetime.utcfromtimestamp(result['message']['expiresIn'] / 1000))
                            guser.subject_id = s.SWS.getGBOUserId(guser)
                            guser.save()
                    gbouser = GBOUser.objects.get(user=user)
                    gbouser.token = result['message']['token'].split(' ')[1]
                    gbouser.validUntil = datetime.utcfromtimestamp(result['message']['expiresIn'] / 1000)
                    #data = s.SWS.getTournamentByUser(gbouser)      
                    gbouser.save()    
                    return redirect("/")
                else:    
                    msg = 'Invalid credentials'    
        else:
            msg = 'Error validating the form'    

    #return redirect("login", {"form": form, "msg" : msg})
    return render(request, "accounts/login.html", {"form": form, "msg" : msg})

def register_user(request):

    msg     = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)

            msg     = 'User created - please <a href="/login">login</a>.'
            success = True
            
            #return redirect("/login/")

        else:
            msg = 'Form is not valid'    
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg" : msg, "success" : success })

class ProfileView(TemplateView):
    template_name = 'page-user.html'

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        context['segment'] = 'profile'
        context['gbo_user'] = GBOUser.objects.filter(user=self.request.user)
        return context