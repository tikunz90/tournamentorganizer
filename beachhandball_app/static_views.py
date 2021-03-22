# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse
from django import template

from .models.Tournament import Tournament, TournamentEvent
from .models.Series import Season

@login_required(login_url="/login/")
def index(request):
    
    context = {}
    context['segment'] = 'index'
    context['segment_title'] = 'Overview'
    context['act_season'] = Season.objects.filter(is_actual=True).first()
    t = Tournament.objects.get(id=1)
    context['tourn'] = t
    context['events'] = TournamentEvent.objects.filter(tournament=t)

    html_template = loader.get_template( 'index.html' )
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def basic_setup(request):
    
    context = {}
    context['segment'] = 'basic_setup'
    context['segment_title'] = 'Basic Setup'
    context['act_season'] = Season.objects.filter(is_actual=True).first()
    t = Tournament.objects.get(id=1)
    context['tourn'] = t
    context['events'] = TournamentEvent.objects.filter(tournament=t)

    html_template = loader.get_template( 'beachhandball/basic_setup.html' )
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def teams_setup(request):
    
    context = {}
    context['segment'] = 'teams_setup'
    context['segment_title'] = 'Teams Setup'
    context['act_season'] = Season.objects.filter(is_actual=True).first()
    t = Tournament.objects.get(id=1)
    context['tourn'] = t
    context['events'] = TournamentEvent.objects.filter(tournament=t)

    html_template = loader.get_template( 'beachhandball/teams_setup.html' )
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def structure_setup(request):
    
    context = {}
    context['segment'] = 'structure_setup'
    context['segment_title'] = 'Structure Setup'
    context['act_season'] = Season.objects.filter(is_actual=True).first()
    t = Tournament.objects.get(id=1)
    context['tourn'] = t
    context['events'] = TournamentEvent.objects.filter(tournament=t)

    html_template = loader.get_template( 'beachhandball/structure_setup.html' )
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def game_plan(request):
    
    context = {}
    context['segment'] = 'game_plan'
    context['segment_title'] = 'Game Plan'
    context['act_season'] = Season.objects.filter(is_actual=True).first()
    t = Tournament.objects.get(id=1)
    context['tourn'] = t
    context['events'] = TournamentEvent.objects.filter(tournament=t)

    html_template = loader.get_template( 'beachhandball/game_plan.html' )
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def results(request):
    
    context = {}
    context['segment'] = 'results'
    context['segment_title'] = 'Results'
    context['act_season'] = Season.objects.filter(is_actual=True).first()
    t = Tournament.objects.get(id=1)
    context['tourn'] = t
    context['events'] = TournamentEvent.objects.filter(tournament=t)

    html_template = loader.get_template( 'beachhandball/results.html' )
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        
        load_template      = request.path.split('/')[-1]
        context['segment'] = load_template
        
        html_template = loader.get_template( load_template )
        return HttpResponse(html_template.render(context, request))
        
    except template.TemplateDoesNotExist:

        html_template = loader.get_template( 'page-404.html' )
        return HttpResponse(html_template.render(context, request))

    except:
    
        html_template = loader.get_template( 'page-500.html' )
        return HttpResponse(html_template.render(context, request))
