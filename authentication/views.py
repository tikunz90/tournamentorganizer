# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from django.forms.models import model_to_dict

#from beachhandball_app.tasks import update_user_tournament_events_async
from beachhandball_app import helper
from beachhandball_app.models.Tournaments import Tournament
from beachhandball_app.models.Series import Season
from django.shortcuts import render
from datetime import datetime
import time

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, Group, Permission
from authentication.models import GBOUser, GBOUserSerializer, LiveScoreUser
from django.forms.utils import ErrorList
from django.http import HttpResponse
from .forms import LoginForm,LoginNoSeasonForm, SignUpForm, SelectTournamentForm
from django.views.generic import TemplateView

#from .tasks import auth_debug_task

from beachhandball_app.services.services import SWS

from django.core.cache import cache

def login_view(request):
    begin_func = time.time()

    seasons = SWS.getSeasonActiveAll()
    # Check for error in seasons response
    if isinstance(seasons, dict) and seasons.get('isError'):
        msg = "Error fetching active seasons from server."
        # Optionally, include status code in the message for debugging
        if 'status_code' in seasons:
            msg += f" (Status code: {seasons['status_code']})"
        form = LoginNoSeasonForm(request.POST or None)
        execution_time_func = time.time() - begin_func
        print('Login execution_time = ' + str(execution_time_func))
        return render(request, "accounts/login_no_season.html", {"form": form, "msg": msg })

    helper.update_active_seasons(seasons)
    seasons = Season.objects.filter(is_actual=True)
    #form = LoginForm(request.POST or None, seasons=seasons)
    form = LoginNoSeasonForm(request.POST or None)

    msg = None
    
    group_tournament_organizer = 'tournament_organizer'
    group_livescore = 'livescore'
    group_scoreboard = 'scoreboard'

    if request.method == "POST":

        if form.is_valid():
            # get token from gbo
            #season_id = int(form.cleaned_data.get("season"))
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            #season_active = [s for s in seasons if s['id'] == season_id][0]

            # check if gbo user is online
            users = User.objects.filter(username=username)
            if users.count() > 0:
                user = users.first()
                is_to = user.groups.filter(name=group_tournament_organizer).exists()
                is_live = user.groups.filter(name=group_livescore).exists()
                if is_to:
                    gbouser = GBOUser.objects.filter(user__username=username).first()
                elif is_live:
                    user = authenticate(username=username, password=password)
                    if user is not None:
                        lsuser = LiveScoreUser.objects.get(user=user)
                        return redirect("live_score")
                    else:
                        msg = 'Invalid credentials'
                        gbouser = None
            else:
                gbouser = None
            
            
            if gbouser:
                if not gbouser.is_online:
                    user = authenticate(username=username, password=password)
                    #if user is not None:
                        # t = Tournament.objects.filter(organizer_orm=gbouser, season__gbo_season_id=season_id)
                        # if t.count() <= 0:
                        #     msg ='No Tournament Data available! SubjectID: ' + str(gbouser.subject_id)
                        #     return render(request, "accounts/login.html", {"form": form, "msg" : msg})
                        # elif t.count() == 1:
                        #     tourn = t.first()
                        #     tourn.is_active = True
                        #     tourn.save()
                        # elif t.count() > 1:
                        #     for tourn in t:
                        #         tourn.is_active = False
                        #         tourn.save()
                        #     login(request, user)
                        #     return redirect("login_select_season_tourn", season_id=season_id)
                    if user is None:
                        msg ='Username or password wrong!'
                        return render(request, "accounts/login_no_season.html", {"form": form, "msg" : msg})
                    login(request, user)
                    return redirect("tournament_setup")


            result = SWS.create_session(username, password)
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
                    guser.subject_id = SWS.getGBOUserId(guser)
                    ##guser.season_active = season_active
                    #guser.gbo_data_all, execution_time = SWS.syncAllTournamentData(guser)
                    ##guser.gbo_data_all, execution_time = SWS.syncTournamentData(guser, season_id)
                    #guser.gbo_data = s.SWS.getTournamentByUser(guser)
                    ##guser.gbo_gc_data, execution_time2 = SWS.syncTournamentGCData(guser, season_id)
                    #guser.gbo_sub_data = s.SWS.getTournamentSubByUser(guser)
                    guser.save()
                    
                
                user = authenticate(username=username, password=password)

                if user is not None:
                    #check if user is TO
                    to_group, cr = Group.objects.get_or_create(name='tournament_organizer')
                    if cr:
                        add_permissions_to(to_group)
                    # add permissions to to_group
                    to_group.user_set.add(user)
                    to_group.save()
                
                    # create gbo user for admin
                    if user.is_superuser is True:
                        if GBOUser.objects.filter(user=user).count() == 0:
                            guser = GBOUser(user=user,
                            gbo_user=result['message']['user']['email'],
                            token = result['message']['token'].split(' ')[1],
                            validUntil = datetime.utcfromtimestamp(result['message']['expiresIn'] / 1000))
                            guser.subject_id = SWS.getGBOUserId(guser)
                            guser.save()
                    
                    gbouser = GBOUser.objects.get(user=user)
                    if gbouser:
                        if gbouser.is_online:
                            gbouser.token = result['message']['token'].split(' ')[1]
                            gbouser.validUntil = datetime.utcfromtimestamp(result['message']['expiresIn'] / 1000)
                            ##gbouser.season_active = season_active
                            #gbouser.subject_id =45
                            #gbouser.gbo_data_all, execution_time = s.SWS.syncAllTournamentData(gbouser)
                            ##gbouser.gbo_data_all, execution_time = SWS.syncTournamentData(gbouser, season_id)
                            #gbouser.gbo_data, execution_time1 = s.SWS.syncTournamentData(gbouser)
                            ##gbouser.gbo_gc_data, execution_time2 = SWS.syncTournamentGCData(gbouser, season_id)
                            #gbouser.gbo_sub_data, execution_time3 = s.SWS.syncTournamentSubData(gbouser)
                            #print('Executiontime syncAllTournamentData: ' + str(execution_time))
                            #print('Executiontime syncTournamentData: ' + str(execution_time1))
                            #print('Executiontime syncTournamentGCData: ' + str(execution_time2))
                            #print('Executiontime syncTournamentSubData: ' + str(execution_time3))
                            
                            helper.update_user_with_gbo(gbouser)
                            gbouser.save() 
                            tourns, execution_time = helper.update_user_tournament(gbouser, seasons)
                        
                        # if len(tourns) <= 0:
                        #     msg ='No Tournament Data available! SubjectID: ' + str(gbouser.subject_id)
                        #     return render(request, "accounts/login.html", {"form": form, "msg" : msg})
                        # elif len(tourns) == 1:
                        #     tourn = tourns[0]
                        #     tourn.is_active = True
                        #     tourn.save()
                            
                        #     # Create livescore user
                            
                        #     update_user_tournament_events(gbouser, tourn)
                        #     #update_user_tournament_events_async.delay(model_to_dict(gbouser), model_to_dict(tourn))
                        # elif len(tourns) > 1:
                        #     for tourn in tourns:
                        #         tourn.is_active = False
                        #         tourn.save()
                        #     login(request, user)
                        #     execution_time_func = time.time() - begin_func
                        #     print('Login execution_time = ' + str(execution_time_func))
                        #     return redirect("login_select_season_tourn", season_id=season_id)

                    else:
                        msg ='GBO user not found! Username: '+ user.username
                        return render(request, "accounts/login_no_season.html", {"form": form, "msg" : msg}) 
                    
                    login(request, user)
                    return redirect("tournament_setup")
                else:    
                    msg = 'Invalid credentials'
            else:
                msg ='GBO session failed!'
                return render(request, "accounts/login_no_season.html", {"form": form, "msg" : msg})
        else:
            msg = 'Error validating the form'    

    execution_time_func = time.time() - begin_func
    print('Login execution_time = ' + str(execution_time_func))
    #return redirect("login", {"form": form, "msg" : msg})
    return render(request, "accounts/login_no_season.html", {"form": form, "msg" : msg, "season": ''})


def select_tourn_view(request):
    guser = GBOUser.objects.filter(user=request.user).first()
    
    msg = None
    form = None
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
            helper.update_user_tournament_events(guser, tourn)
            #update_user_tournament_events_async.delay(model_to_dict(guser), model_to_dict(tourn))
            return redirect('/')

    #return redirect("login", {"form": form, "msg" : msg})
    return render(request, "accounts/login_select_tourn.html", {"form": form, "msg" : msg})


def select_season_tourn_view(request, season_id):
    guser = GBOUser.objects.filter(user=request.user).first()
    context = {'gbouser': guser, 'form': None, 'msg': '', 'seasons': [], 'tournaments':{}}
    if request.method == "GET":
        print("select_tourn_view GET")
        context['form'] = SelectTournamentForm(request.GET, gbo_organizer=guser.subject_id, season_id=season_id)
        
    if request.method == "POST":
        context['form'] = SelectTournamentForm(request.POST, gbo_organizer=guser.subject_id, season_id=season_id)
        if context['form'].is_valid():
            print("select_tourn_view POST tourn:" + request.POST['tournaments'])
            id_tourn = request.POST['tournaments']
            tourn = Tournament.objects.get(id=id_tourn)
            tourn.is_active = True
            tourn.save()
            helper.update_user_tournament_events(guser, tourn)
            #update_user_tournament_events_async.delay(model_to_dict(guser), model_to_dict(tourn))
            return redirect('/')

    #return redirect("login", {"form": form, "msg" : msg})
    return render(request, "accounts/login_select_season_tourn.html", context)



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


def add_permissions_to(to_group):
    #p1 = Permission.objects.get(codename='beachhandball_app.can_add_court')
    #p2 = Permission.objects.get(codename='beachhandball_app.can_change_court')
    #p3 = Permission.objects.get(codename='beachhandball_app.can_delete_court')
    #p4 = Permission.objects.get(codename='beachhandball_app.can_view_court')
    #
    #to_group.permissions.add(p1, p2, p3, p4)
    do_nothing = 1
    
class ProfileView(TemplateView):
    template_name = 'page-user.html'

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        context['segment'] = 'profile'
        context['segment_title'] = 'Profile'
        context['gbo_user'] = GBOUser.objects.filter(user=self.request.user).first()
        return context

