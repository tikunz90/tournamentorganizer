# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from beachhandball_app import static_views
from beachhandball_app.views.teams_setup import TeamsSetupDetail

from django.views.generic import TemplateView

urlpatterns = [

    # The home page
    path('', static_views.index, name='index'),
    path('basic_setup/', static_views.basic_setup, name='basic_setup'),

    path('teams_setup/', static_views.teams_setup, name='teams_setup'),
    path('teams_setup/<int:pk>/', TeamsSetupDetail.as_view(), name='teams_setup.detail'),

    path('structure_setup/', static_views.structure_setup, name='structure_setup'),
    path('game_plan/', static_views.game_plan, name='game_plan'),
    path('results/', static_views.results, name='results'),

]
