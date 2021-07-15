# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from beachhandball_app import static_views
from beachhandball_app.views.basic_setup import CourtCreateView, CourtUpdateView, CourtDeleteView
from beachhandball_app.views.teams_setup import TeamsSetupDetail
from beachhandball_app.views.structure_setup import DownloadPreGameView, DownloadPreGameAllView, GameCreateView, GameResultGameView, GameUpGameView, StateFinishView, StructureSetupDetail, StageCreateView, StageDeleteView, StateCreateView, StateDeleteView, StateUpdateView, TTTUpdateView, TeamStatsUpdateTeamView, GameDeleteView, TournamentStageDetail
from beachhandball_app.views.structure_setup_fb import games_list
from beachhandball_app.views.results import ResultsDetail

from django.views.generic import TemplateView

urlpatterns = [

    # The home page
    path('', static_views.index, name='index'),
    #re_path(r'^.*\.*', static_views.pages, name='pages'),
    path('ajax/data/', static_views.getData, name='get_data'),

    path('sync_tournament_data/', static_views.sync_tournament_data, name='sync_tournament_data'),

    path('game_plan/ajax/update-game-date/<int:pk>/', static_views.UpdateGameFromList.as_view(), name='ajax-update-game-date'),
    path('game_plan/ajax/update-game-court/<int:pk>/', static_views.UpdateGameCourtFromList.as_view(), name='ajax-update-game-court'),

    path('basic_setup/', static_views.basic_setup, name='basic_setup'),
    path('basic_setup/<int:pk_tourn>/create_court/', CourtCreateView.as_view(), name='basic_setup.create_court'),
    path('basic_setup/<int:pk_tourn>/update_court/<int:pk>/', CourtUpdateView.as_view(), name='basic_setup.update_court'),
    path('basic_setup/<int:pk_tourn>/delete_court/<int:pk>/', CourtDeleteView.as_view(), name='basic_setup.delete_court'),

    path('teams_setup/', static_views.teams_setup, name='teams_setup'),
    path('teams_setup/<int:pk>/', TeamsSetupDetail.as_view(), name='teams_setup.detail'),

    path('structure_setup/', static_views.structure_setup, name='structure_setup'),
    path('structure_setup/<int:pk>/', StructureSetupDetail.as_view(), name='structure_setup.detail'),
    #path('structure_setup/<int:pk>/create_tstage/', StructureSetupCreateTournamentStage.as_view(), name='structure_setup.create_tstage'),
    path('structure_setup/<int:pk>/create_tstage/', StageCreateView.as_view(), name='structure_setup.create_tstage'),
    path('structure_setup/<int:pk_tevent>/delete_tstage/<int:pk>/', StageDeleteView.as_view(), name='structure_setup.delete_tstage'),
    path('structure_setup/<int:pk_tevent>/<int:pk_tstage>/create_state', StateCreateView.as_view(), name='structure_setup.create_tstate'),
    path('structure_setup/<int:pk_tevent>/<int:pk>/tstage_printview', TournamentStageDetail.as_view(), name='structure_setup.tstage_printview'),
    path('structure_setup/<int:pk_tevent>/<int:pk_tstage>/delete_tstate/<int:pk>/', StateDeleteView.as_view(), name='structure_setup.delete_tstate'),
    path('structure_setup/<int:pk_tevent>/<int:pk_tstage>/update_tstate/<int:pk>/', StateUpdateView.as_view(), name='structure_setup.update_tstate'),
    path('structure_setup/<int:pk_tevent>/<int:pk_tstage>/finish_tstate/<int:pk>/', StateFinishView.as_view(), name='structure_setup.finish_tstate'),
    path('structure_setup/<int:pk_tevent>/<int:pk_tstage>/update_teamstatsteam/<int:pk>/', TeamStatsUpdateTeamView.as_view(), name='structure_setup.update_teamstatsteam'),
    path('structure_setup/<int:pk_tevent>/<int:pk_tstage>/update_tttransition/<int:pk>/', TTTUpdateView.as_view(), name='structure_setup.update_tttransition'),
    path('structure_setup/<int:pk_tevent>/<int:pk_tstage>/<int:pk_tstate>/create_game/', GameCreateView.as_view(), name='structure_setup.create_game'),
    path('structure_setup/<int:pk_tevent>/<int:pk_tstage>/update_game/<int:pk>/', GameUpGameView.as_view(), name='structure_setup.update_game'),
    path('structure_setup/<int:pk_tevent>/<int:pk_tstage>/delete_game/<int:pk>/', GameDeleteView.as_view(), name='structure_setup.delete_game'),
    path('structure_setup/<int:pk_tstate>/games/', games_list, name='games_list'),
    path('structure_setup/<int:pk_tevent>/<int:pk_tstage>/update_game/<int:pk>', GameUpGameView.as_view(), name='update_game'),
    path('structure_setup/<int:pk_tevent>/<int:pk_tstage>/update_game_result/<int:pk>', GameResultGameView.as_view(), name='update_game_result'),
    path('structure_setup/<int:pk_tevent>/<int:pk_tstage>/download_pre_game/<int:pk>', DownloadPreGameView.as_view(), name='download_pre_game'),
    path('structure_setup/<int:pk_tevent>/<int:pk_tstage>/download_pre_game_all/<int:pk>', DownloadPreGameAllView.as_view(), name='download_pre_game_all'),
    

    path('game_plan/', static_views.game_plan, name='game_plan'),
    path('results/', static_views.results, name='results'),
    path('results/<int:pk>/', ResultsDetail.as_view(), name='results.detail'),

    path('team_testdata/<int:pk_tevent>/', static_views.create_teamtestdata, name='team_testdata'),

]
