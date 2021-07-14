# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from beachhandball_app.models.Tournaments import Tournament
from django.shortcuts import render
from datetime import datetime

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, Group
from authentication.models import GBOUser
from django.forms.utils import ErrorList
from django.http import HttpResponse
from .forms import LoginForm, SignUpForm, SelectTournamentForm
from django.views.generic import TemplateView

from .tasks import auth_debug_task

from beachhandball_app.services import services as s
from beachhandball_app.helper import update_user_tournament, update_user_tournament_events

from django.core.cache import cache

def login_view(request):
    form = LoginForm(request.POST or None)

    msg = None
    cache.set('foo', 'bar')
    auth_debug_task.delay('HELLO')

    if request.method == "POST":

        if form.is_valid():
            # get token from gbo
            print()
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            # check if gbo user is online
            user = User.objects.filter(username=username)
            if user.count() > 0:
                gbouser = GBOUser.objects.filter(user__username=username).first()
            else:
                gbouser = None
            if gbouser:
                if not gbouser.is_online:
                    user = authenticate(username=username, password=password)
                    if user is not None:
                        t = Tournament.objects.filter(organizer=gbouser.subject_id)
                        if t.count() <= 0:
                            msg ='No Tournament Data available! SubjectID: ' + str(gbouser.subject_id)
                            return render(request, "accounts/login.html", {"form": form, "msg" : msg})
                        elif t.count() == 1:
                            tourn = t.first()
                            tourn.is_active = True
                            tourn.save()
                        elif t.count() > 1:
                            for tourn in t:
                                tourn.is_active = False
                                tourn.save()
                            login(request, user)
                            return redirect("login_select_tourn")
                    else:
                        msg ='Username or password wrong!'
                        return render(request, "accounts/login.html", {"form": form, "msg" : msg})
                    login(request, user)
                    return redirect("/")


            result = s.SWS.create_session(username, password)
            if result['isError'] is not True:
                # first login => create gbo user
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
                    guser.gbo_data = s.SWS.getTournamentByUser(guser)
                    guser.gbo_gc_data = s.SWS.getTournamentGermanChampionshipByUser(guser)
                    guser.gbo_sub_data = s.SWS.getTournamentSubByUser(guser)
                    guser.save()
                    to_group = Group.objects.get(name='tournament_organizer')
                    to_group.user_set.add(user)
                
                user = authenticate(username=username, password=password)
                if user is not None:
                    # create gbo user for admin
                    if user.is_superuser is True:
                        if GBOUser.objects.filter(user=user).count() == 0:
                            guser = GBOUser(user=user,
                            gbo_user=result['message']['user']['email'],
                            token = result['message']['token'].split(' ')[1],
                            validUntil = datetime.utcfromtimestamp(result['message']['expiresIn'] / 1000))
                            guser.subject_id = s.SWS.getGBOUserId(guser)
                            guser.save()
                    
                    gbouser = GBOUser.objects.get(user=user)
                    if gbouser:
                        if gbouser.is_online:
                            gbouser.token = result['message']['token'].split(' ')[1]
                            gbouser.validUntil = datetime.utcfromtimestamp(result['message']['expiresIn'] / 1000)

                            #gbouser.subject_id =45

                            gbouser.gbo_data = s.SWS.syncTournamentData(gbouser)
                            gbouser.gbo_gc_data = s.SWS.syncTournamentGCData(gbouser)
                            gbouser.gbo_sub_data = s.SWS.syncTournamentSubData(gbouser)
                            gbouser.save() 
                        
                        update_user_tournament(gbouser)
                        t = Tournament.objects.filter(organizer=gbouser.subject_id)
                        
                        if t.count() <= 0:
                            msg ='No Tournament Data available! SubjectID: ' + str(gbouser.subject_id)
                            return render(request, "accounts/login.html", {"form": form, "msg" : msg})
                        elif t.count() == 1:
                            tourn = t.first()
                            tourn.is_active = True
                            tourn.save()
                            #update_user_tournament_events(gbouser, tourn)
                        elif t.count() > 1:
                            for tourn in t:
                                tourn.is_active = False
                                tourn.save()
                            login(request, user)
                            return redirect("login_select_tourn")

                    else:
                        msg ='GBO user not found! Username: '+ user.username
                        return render(request, "accounts/login.html", {"form": form, "msg" : msg}) 
                    
                    login(request, user)
                    return redirect("/")
                else:    
                    msg = 'Invalid credentials'
            else:
                msg ='GBO session failed!'
                return render(request, "accounts/login.html", {"form": form, "msg" : msg})
        else:
            msg = 'Error validating the form'    

    #return redirect("login", {"form": form, "msg" : msg})
    return render(request, "accounts/login.html", {"form": form, "msg" : msg})


def select_tourn_view(request):
    guser = GBOUser.objects.filter(user=request.user).first()
    

    msg = None

    if request.method == "GET":
        print("select_tourn_view GET")
        form = SelectTournamentForm(request.GET, gbo_organizer=guser.subject_id)
    if request.method == "POST":
        form = SelectTournamentForm(request.POST, gbo_organizer=guser.subject_id)
        if form.is_valid():
            print("select_tourn_view POST tourn:" + request.POST['tournaments'])
            id_tourn = request.POST['tournaments']
            tourn = Tournament.objects.get(id=id_tourn)
            tourn.is_active = True
            tourn.save()
            update_user_tournament_events(guser, tourn)
            return redirect('/')

    #return redirect("login", {"form": form, "msg" : msg})
    return render(request, "accounts/login_select_tourn.html", {"form": form, "msg" : msg})


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

