# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from beachhandball_app import static_views
from beachhandball_app.views.teams_setup import TeamsSetupDetail
from beachhandball_app.views.structure_setup import GameUpGameView, StructureSetupDetail, StageCreateView, StageDeleteView, StateCreateView, StateDeleteView, StateUpdateView, TTTUpdateView, TeamStatsUpdateTeamView

from django.views.generic import TemplateView

urlpatterns = [

    # The home page
    path('', static_views.index, name='index'),
    #re_path(r'^.*\.*', static_views.pages, name='pages'),
    path('ajax/data/', static_views.getData, name='get_data'),

    path('basic_setup/', static_views.basic_setup, name='basic_setup'),

    path('teams_setup/', static_views.teams_setup, name='teams_setup'),
    path('teams_setup/<int:pk>/', TeamsSetupDetail.as_view(), name='teams_setup.detail'),

    path('structure_setup/', static_views.structure_setup, name='structure_setup'),
    path('structure_setup/<int:pk>/', StructureSetupDetail.as_view(), name='structure_setup.detail'),
    #path('structure_setup/<int:pk>/create_tstage/', StructureSetupCreateTournamentStage.as_view(), name='structure_setup.create_tstage'),
    path('structure_setup/<int:pk>/create_tstage/', StageCreateView.as_view(), name='structure_setup.create_tstage'),
    path('structure_setup/<int:pk_tevent>/delete_tstage/<int:pk>/', StageDeleteView.as_view(), name='structure_setup.delete_tstage'),
    path('structure_setup/<int:pk_tevent>/<int:pk_tstage>/create_state', StateCreateView.as_view(), name='structure_setup.create_tstate'),
    path('structure_setup/<int:pk_tevent>/<int:pk_tstage>/delete_tstate/<int:pk>/', StateDeleteView.as_view(), name='structure_setup.delete_tstate'),
    path('structure_setup/<int:pk_tevent>/<int:pk_tstage>/update_tstate/<int:pk>/', StateUpdateView.as_view(), name='structure_setup.update_tstate'),
    path('structure_setup/<int:pk_tevent>/<int:pk_tstage>/update_teamstatsteam/<int:pk>/', TeamStatsUpdateTeamView.as_view(), name='structure_setup.update_teamstatsteam'),
    path('structure_setup/<int:pk_tevent>/<int:pk_tstage>/update_tttransition/<int:pk>/', TTTUpdateView.as_view(), name='structure_setup.update_tttransition'),
    path('structure_setup/<int:pk_tevent>/<int:pk_tstage>/update_game/<int:pk>/', GameUpGameView.as_view(), name='structure_setup.update_game'),
    path('structure_setup/<int:pk_tstate>/games/', static_views.game_update, name='game_update_async'),
    path('update_game/<int:pk_tevent>/<int:pk_tstage>/<int:pk>', GameUpGameView.as_view(), name='update_game'),
    

    path('game_plan/', static_views.game_plan, name='game_plan'),
    path('results/', static_views.results, name='results'),

]
