from django.urls import reverse
# from beachhandball_app.tasks import update_user_tournament_events_async
from datetime import datetime
import time
import json
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.db.models.query import Prefetch
from django.forms.models import model_to_dict
from rest_framework.renderers import JSONRenderer
from django.utils.dateparse import parse_datetime
from django.contrib import messages
from django.contrib.messages import get_messages

from django.views.generic import TemplateView
from beachhandball_app import helper, wizard
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django import template
from django.db.models import Q

from authentication.models import GBOUser, ScoreBoardUser
from .models.Tournaments import Court, Referee, Tournament, TournamentEvent, TournamentSettings, TournamentStage, TournamentState
from .models.Team import Team, TeamStats
from .models.Player import Player
from .models.Series import Season
from .models.Game import Game
from beachhandball_app.forms.basic_setup.forms import CourtForm, TournamentSettingsForm
from beachhandball_app.api.serializers.game import GameSerializer,GameRunningSerializer, serialize_game
from beachhandball_app.game_report import helper_game_report
from .services.services import SWS

def getContext(request):
    print('Enter getContext' , datetime.now())
    context = {}

    guser = GBOUser.objects.filter(user=request.user).first()
    
    if guser is None:
        return context
    else:
        context['gbo_user'] = guser
        context['season_active'] = guser.season_active['name'] #SWS.getSeasonActive(guser)
        context['token'] = guser.token
    
    t = Tournament.objects.prefetch_related(
        Prefetch("tournamentsettings_set", queryset=TournamentSettings.objects.all(), to_attr="settings"), 
        Prefetch("tournamentevent_set", queryset=TournamentEvent.objects.all(), to_attr="events")).get(organizer=guser.subject_id, is_active=True, season__gbo_season_id=guser.season_active['id'])
    context['tourn'] = t
    context['tourn_settings'] = t.settings[0] #TournamentSettings.objects.get(tournament=t)
    context['events'] = t.events #TournamentEvent.objects.filter(tournament=t)
    print('Exit getContext', datetime.now())
    return context

def checkLoginIsValid(gbouser):
    if not gbouser.is_online:
        return True
    if int(time.time()) > time.mktime(gbouser.validUntil.timetuple()):
        return False
    else:
        return True

def getData(request):
    t = Tournament.objects.get(id=1)
    tevent = TournamentEvent.objects.filter(tournament=t).first();
    tstates = list(TournamentState.objects.filter(tournament_event=tevent).values())

    for ts in tstates:
        tstats = TeamStats.objects.filter(tournamentstate=ts['id'])
        ts['tstats'] = list(tstats.values())
        for stat in ts['tstats']:
            team = Team.objects.filter(id=stat['team_id']).first()
            stat['team_name'] = team.name
    data = {
        'teams': list(Team.objects.all().filter(tournament_event=tevent).values()),
        'tstates': tstates
    }
    

    return JsonResponse(data)


#@login_required(login_url="/login/")
#@user_passes_test(lambda u: u.groups.filter(name='livescore').exists(),
#login_url="/login/", redirect_field_name='livescore')
def livescore_overview(request, pk_tourn):
    
    #context = getContext(request)
    #if not checkLoginIsValid(context['gbo_user']):
    #    return redirect('login')
    context = {}
    #context['segment'] = 'livescore'
    #context['segment_title'] = 'Livescore'
    orderbyList  = ['starttime','court__name']
    t = Tournament.objects.prefetch_related(
            Prefetch("game_set", queryset=Game.objects.select_related("tournament", "tournament_event__category", "team_a", "team_b", "team_st_a__team", "team_st_b__team", "ref_a", "ref_b", "tournament_state__tournament_stage", "court").order_by(*orderbyList).prefetch_related(
            "team_a__player_set",
            "team_b__player_set"
             )
                , to_attr="all_games"),
            Prefetch("tournamentevent_set", queryset=TournamentEvent.objects.select_related("tournament", "category").prefetch_related(
                Prefetch("tournamentstate_set", queryset=TournamentState.objects.select_related("tournament_event__category", "tournament_stage")
                , to_attr="all_tstates")
            )
                , to_attr="all_tevents"),
            Prefetch("court_set", queryset=Court.objects.select_related("tournament")
                , to_attr="all_courts"),
            Prefetch("referee_set", queryset=Referee.objects.select_related("tournament")
                , to_attr="all_refs")
                ).get(id=pk_tourn)
    context['tourn'] = t
    #context['tourn_settings'] = t.settings[0] #TournamentSettings.objects.get(tournament=t)
    context['events'] = t.all_tevents #TournamentEvent.objects.filter(tournament=t)

    context['mqtt_broker'] = settings.MQTT_BROKER
    context['mqtt_port'] = settings.MQTT_PORT
    
    html_template = loader.get_template( 'livescore/livescore_overview.html' )
    return HttpResponse(html_template.render(context, request))


#@login_required(login_url="/login/")
#@user_passes_test(lambda u: u.groups.filter(name='livescore').exists(),
#login_url="/login/", redirect_field_name='livescore')
def livescore_tickeronly(request):
    
    #context = getContext(request)
    #if not checkLoginIsValid(context['gbo_user']):
    #    return redirect('login')
    context = {}
    
    game = Game()

    context['tournament_id'] = 0
    context['court_id'] = 0
    #context['game'] = game
    context['mqtt_broker'] = settings.MQTT_BROKER
    context['mqtt_port'] = settings.MQTT_PORT
    
    html_template = loader.get_template( 'livescore/livescore_tickeronly.html' )
    return HttpResponse(html_template.render(context, request))


#@login_required(login_url="/login/")
#@user_passes_test(lambda u: u.groups.filter(name='livescore').exists(),
#login_url="/login/", redirect_field_name='livescore')
def livescore_display_livestream_old(request, pk_tourn, pk_court):
    
    #context = getContext(request)
    #if not checkLoginIsValid(context['gbo_user']):
    #    return redirect('login')
    context = {}
    #context['segment'] = 'livescore'
    #context['segment_title'] = 'Livescore'
    orderbyList  = ['starttime','court__name']
    t = Tournament.objects.prefetch_related(
            Prefetch("game_set", queryset=Game.objects.select_related("tournament", "tournament_event__category", "team_a", "team_b", "team_st_a__team", "team_st_b__team", "ref_a", "ref_b", "tournament_state__tournament_stage", "court").order_by(*orderbyList).prefetch_related(
            "team_a__player_set",
            "team_b__player_set"
             )
                , to_attr="all_games"),
            Prefetch("tournamentevent_set", queryset=TournamentEvent.objects.select_related("tournament", "category").prefetch_related(
                Prefetch("tournamentstate_set", queryset=TournamentState.objects.select_related("tournament_event__category", "tournament_stage")
                , to_attr="all_tstates")
            )
                , to_attr="all_tevents"),
            Prefetch("court_set", queryset=Court.objects.select_related("tournament")
                , to_attr="all_courts"),
            Prefetch("referee_set", queryset=Referee.objects.select_related("tournament")
                , to_attr="all_refs")
                ).get(id=pk_tourn)
    context['tourn'] = t
    #context['tourn_settings'] = t.settings[0] #TournamentSettings.objects.get(tournament=t)
    context['events'] = t.all_tevents #TournamentEvent.objects.filter(tournament=t)

    html_template = loader.get_template( 'livescore/livescore_display_livestream.html' )
    return HttpResponse(html_template.render(context, request))

def livescore_display_livestream(request, pk_tourn, pk_court):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        t = Tournament.objects.get(season_cup_tournament_id=pk_tourn)
        game = Game.objects.filter(tournament = t, court_id=pk_court).first()
        context['tournament_id'] = pk_tourn
        context['court_id'] = pk_court
        context['game'] = game
        
        context['mqtt_broker'] = settings.MQTT_BROKER
        context['mqtt_port'] = settings.MQTT_PORT

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('livescore/livescore_display_livestream.html')
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('page-404.html')
        return HttpResponse(html_template.render(context, request))

    except Exception as e:
        print(e)
        html_template = loader.get_template('page-500.html')
        return HttpResponse(html_template.render(context, request))
    

def livescore_display_livestream_teaminfo(request, pk_tourn, pk_court):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        t = Tournament.objects.get(season_cup_tournament_id=pk_tourn)
        #game = Game.objects.filter(tournament = t, court_id=pk_court).first()
        #game = Game.objects.prefetch_related("team_a__player_set",
        #    "team_b__player_set").filter(tournament = t, court_id=pk_court, gamestate='RUNNING').first()
        #if game is None:
        #    game = Game.objects.prefetch_related("team_a__player_set",
        #    "team_b__player_set").filter(tournament = t, court_id=pk_court, gamestate='APPENDING').first()
        
        game = Game.objects.prefetch_related(
                Prefetch('team_a__player_set', queryset=Player.objects.filter(is_active=True), to_attr='active_players'),
                Prefetch('team_b__player_set', queryset=Player.objects.filter(is_active=True), to_attr='active_players')
            ).filter(
                tournament=t,
                court_id=pk_court,
                gamestate='RUNNING'
            ).first()
        
        if game is None:
            game = Game.objects.prefetch_related("team_a__player_set",
            "team_b__player_set").filter(tournament = t, court_id=pk_court, gamestate='APPENDING').first()
            game = Game.objects.prefetch_related(
                    Prefetch('team_a__player_set', queryset=Player.objects.filter(is_active=True), to_attr='active_players'),
                    Prefetch('team_b__player_set', queryset=Player.objects.filter(is_active=True), to_attr='active_players')
                ).filter(
                    tournament=t,
                    court_id=pk_court,
                    gamestate='APPENDING'
                ).first()
        
        
        
        
        context['tournament_id'] = pk_tourn
        context['court_id'] = pk_court
        context['game'] = game
        context['players_a'] = game.team_a.active_players
        context['players_b'] = game.team_b.active_players

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('livescore/livescore_display_livestream_teaminfo.html')
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('page-404.html')
        return HttpResponse(html_template.render(context, request))

    except Exception as e:
        print(e)
        html_template = loader.get_template('page-500.html')
        return HttpResponse(html_template.render(context, request))
    

def livescore_display_big_scoreboard(request, pk_tourn, pk_court):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        t = Tournament.objects.get(season_cup_tournament_id=pk_tourn)
        game = Game.objects.filter(tournament = t, court_id=pk_court).first()
        context['tournament_id'] = pk_tourn
        context['court_id'] = pk_court
        context['game'] = game
        
        context['mqtt_broker'] = settings.MQTT_BROKER
        context['mqtt_port'] = settings.MQTT_PORT

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('livescore/livescore_display_big_scoreboard.html')
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('page-404.html')
        return HttpResponse(html_template.render(context, request))

    except Exception as e:
        print(e)
        html_template = loader.get_template('page-500.html')
        return HttpResponse(html_template.render(context, request))
    

def livescore_ledwall(request, pk_tourn, pk_court):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        t = Tournament.objects.get(season_cup_tournament_id=pk_tourn)
        #game = Game.objects.filter(tournament = t, court_id=pk_court).first()
        #game = Game.objects.prefetch_related("team_a__player_set",
        #    "team_b__player_set").filter(tournament = t, court_id=pk_court, gamestate='RUNNING').first()
        
        game = Game.objects.prefetch_related(
                Prefetch('team_a__player_set', queryset=Player.objects.filter(is_active=True), to_attr='active_players'),
                Prefetch('team_b__player_set', queryset=Player.objects.filter(is_active=True), to_attr='active_players')
            ).filter(
                tournament=t,
                court_id=pk_court,
                gamestate='RUNNING'
            ).first()
        
        if game is None:
            game = Game.objects.prefetch_related("team_a__player_set",
            "team_b__player_set").filter(tournament = t, court_id=pk_court, gamestate='APPENDING').first()
            game = Game.objects.prefetch_related(
                    Prefetch('team_a__player_set', queryset=Player.objects.filter(is_active=True), to_attr='active_players'),
                    Prefetch('team_b__player_set', queryset=Player.objects.filter(is_active=True), to_attr='active_players')
                ).filter(
                    tournament=t,
                    court_id=pk_court,
                    gamestate='APPENDING'
                ).first()
            
        context['tournament_id'] = pk_tourn
        context['court_id'] = pk_court
        context['game'] = game
        context['players_a'] = game.team_a.active_players
        context['players_b'] = game.team_b.active_players

        context['mqtt_broker'] = settings.MQTT_BROKER
        context['mqtt_port'] = settings.MQTT_PORT

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('livescore/led_wall.html')
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('page-404.html')
        return HttpResponse(html_template.render(context, request))

    except Exception as e:
        print(e)
        html_template = loader.get_template('page-500.html')
        return HttpResponse(html_template.render(context, request))
    

def livescore_ledwall_control(request, pk_tourn, pk_court):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        t = Tournament.objects.get(season_cup_tournament_id=pk_tourn)
        #game = Game.objects.filter(tournament = t, court_id=pk_court).first()
        game = Game.objects.prefetch_related("team_a__player_set",
            "team_b__player_set").filter(tournament = t, court_id=pk_court, gamestate='RUNNING').first()
        if game is None:
            game = Game.objects.prefetch_related("team_a__player_set",
            "team_b__player_set").filter(tournament = t, court_id=pk_court, gamestate='APPENDING').first()
        context['tournament_id'] = pk_tourn
        context['court_id'] = pk_court
        context['game'] = game

        context['mqtt_broker'] = settings.MQTT_BROKER
        context['mqtt_port'] = settings.MQTT_PORT

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('livescore/led_wall_control.html')
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('page-404.html')
        return HttpResponse(html_template.render(context, request))

    except Exception as e:
        print(e)
        html_template = loader.get_template('page-500.html')
        return HttpResponse(html_template.render(context, request))