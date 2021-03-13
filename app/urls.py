# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from app import views

from django.views.generic import TemplateView

urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('basic_setup/', views.basic_setup, name='basic_setup'),
    path('teams_setup/', views.teams_setup, name='teams_setup'),
    path('structure_setup/', views.structure_setup, name='structure_setup'),
    path('game_plan/', views.game_plan, name='game_plan'),
    path('results/', views.results, name='results'),

]
