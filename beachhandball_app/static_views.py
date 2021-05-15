# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from beachhandball_app import helper
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse, JsonResponse
from django import template
from django.db.models import Q

from authentication.models import GBOUser
from .models.Tournament import Tournament, TournamentEvent, TournamentState
from .models.Team import Team, TeamStats
from .models.Series import Season
from .models.Game import Game

from .services.services import SWS

def getContext(request):
    context = {}

    guser = GBOUser.objects.filter(user=request.user).first()
    
    if guser is None:
        return context
    else:
        context['gbo_user'] = guser
        context['season_active'] = SWS.getSeasonActive(guser)
        context['token'] = guser.token
    
    t, cr = Tournament.objects.get_or_create(organizer=guser.subject_id)
    if cr:
        t.name = 'Not Named'
    t.save()
    context['tourn'] = t
    context['events'] = TournamentEvent.objects.filter(tournament=t)
    return context

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

def not_in_student_group(user):
    if user:
        return user.groups.filter(name='tournament_organizer').count() == 0
    return False

@login_required(login_url="/login/")
@user_passes_test(lambda u: u.groups.filter(name='tournament_organizer').exists(),
login_url="/login/", redirect_field_name='next')
def index(request):
    context = getContext(request)

    context['segment'] = 'index'
    context['segment_title'] = 'Overview'

    html_template = loader.get_template( 'index.html' )
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
@user_passes_test(lambda u: u.groups.filter(name='tournament_organizer').exists(),
login_url="/login/", redirect_field_name='next')
def basic_setup(request):
    
    context = getContext(request)

    context['segment'] = 'basic_setup'
    context['segment_title'] = 'Basic Setup'

    html_template = loader.get_template( 'beachhandball/basic_setup.html' )
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
@user_passes_test(lambda u: u.groups.filter(name='tournament_organizer').exists(),
login_url="/login/", redirect_field_name='next')
def teams_setup(request):
    
    context = getContext(request)

    context['segment'] = 'teams_setup'
    context['segment_title'] = 'Teams Setup'

    html_template = loader.get_template( 'beachhandball/teams_setup.html' )
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
@user_passes_test(lambda u: u.groups.filter(name='tournament_organizer').exists(),
login_url="/login/", redirect_field_name='next')
def structure_setup(request):
    
    context = getContext(request)

    context['segment'] = 'structure_setup'
    context['segment_title'] = 'Structure Setup'

    html_template = loader.get_template( 'beachhandball/structure_setup.html' )
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
@user_passes_test(lambda u: u.groups.filter(name='tournament_organizer').exists(),
login_url="/login/", redirect_field_name='next')
def game_plan(request):
    
    context = getContext(request)
    tourn = context['tourn']
    tevents = context['events']


    context['segment'] = 'game_plan'
    context['segment_title'] = 'Game Plan'

    html_template = loader.get_template( 'beachhandball/game_plan.html' )
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
@user_passes_test(lambda u: u.groups.filter(name='tournament_organizer').exists(),
login_url="/login/", redirect_field_name='next')
def results(request):
    
    context = getContext(request)

    context['segment'] = 'results'
    context['segment_title'] = 'Results'

    html_template = loader.get_template( 'beachhandball/tournamentevent/results.html' )
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
@user_passes_test(lambda u: u.groups.filter(name='tournament_organizer').exists(),
login_url="/login/", redirect_field_name='next')
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        
        load_template      = request.path.split('/')[-1]
        context['segment'] = load_template
        context['segment_title'] = load_template.split('.')[0]
        html_template = loader.get_template( load_template )
        return HttpResponse(html_template.render(context, request))
        
    except template.TemplateDoesNotExist:

        html_template = loader.get_template( 'page-404.html' )
        return HttpResponse(html_template.render(context, request))

    except Exception as e:
        print(e)
    
        html_template = loader.get_template( 'page-500.html' )
        return HttpResponse(html_template.render(context, request))


def create_teamtestdata(request, pk_tevent):
    context = getContext(request)

    helper.create_teams_testdata(pk_tevent)

    context['segment'] = 'index'
    context['segment_title'] = 'Overview'

    html_template = loader.get_template( 'index.html' )
    return HttpResponse(html_template.render(context, request))

