# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from beachhandball_app import static_views, livescore_views
from beachhandball_app.views.basic_setup import CourtCreateView, CourtUpdateView, CourtDeleteView
from beachhandball_app.views.teams_setup import TeamsSetupDetail
from beachhandball_app.views.structure_setup import DownloadPreGameView, DownloadPreGameAllView, GameCreateView, GameResultGameView, GameUpGameView, StateFinishView, StructureSetupDetail, StageCreateView, StageDeleteView, StateCreateView, StateDeleteView, StateUpdateView, TTTUpdateView, TeamStatsUpdateTeamView, GameDeleteView, TournamentEventDetail, TournamentStageDetail, postUpdateGameResult, update_teamsetup
from beachhandball_app.views.structure_setup_fb import games_list, tstate_add_team, tstate_delete_team
from beachhandball_app.views.results import ResultsDetail

from django.views.generic import TemplateView

urlpatterns = [

    # The home page
    path('', static_views.index, name='index'),
    #path('test', static_views.test, name='test'),
    #re_path(r'^.*\.*', static_views.pages, name='pages'),
    path('ajax/data/', static_views.getData, name='get_data'),

    path('setup-wizard/<int:pk_tevent>/', static_views.setup_wizard, name='setup_wizard'),
    path('setup-wizard/game-plan/', static_views.setup_wizard_gameplan, name='setup_wizard_gameplan'),

    path('sync_tournament_data/', static_views.sync_tournament_data, name='sync_tournament_data'),
    path('recalc_global_stats/<int:pk_tevent>/', static_views.recalc_global_stats, name='recalc_global_stats'),

    path('running_game/<int:pk_tourn>/<int:courtid>/', static_views.running_game, name='game_list'),

    path('game_plan/ajax/update-game-date/<int:pk>/', static_views.UpdateGameFromList.as_view(), name='ajax-update-game-date'),
    path('game_plan/ajax/update-game-after-drag/<int:pk>/', static_views.UpdateGameFromListAfterDrag.as_view(), name='ajax-update-game-after-drag'),
    path('game_plan/ajax/update-game-court/<int:pk>/', static_views.UpdateGameCourtFromList.as_view(), name='ajax-update-game-court'),

    path('basic_setup/', static_views.basic_setup, name='basic_setup'),
    path('basic_setup/<int:pk_tourn>/create_court/', CourtCreateView.as_view(), name='basic_setup.create_court'),
    path('basic_setup/<int:pk_tourn>/update_court/<int:pk>/', CourtUpdateView.as_view(), name='basic_setup.update_court'),
    path('basic_setup/<int:pk_tourn>/delete_court/<int:pk>/', CourtDeleteView.as_view(), name='basic_setup.delete_court'),

    path('teams_setup/', static_views.teams_setup, name='teams_setup'),
    path('teams_setup/<int:pk>/', TeamsSetupDetail.as_view(), name='teams_setup.detail'),

    path('structure_setup/', static_views.structure_setup, name='structure_setup'),
    path('structure_setup/<int:pk>/', StructureSetupDetail.as_view(), name='structure_setup.detail'),
    path('structure_setup/<int:pk_tevent>/delete_structure/', static_views.delete_structure, name='structure_setup.delete_all'),
    #path('structure_setup/<int:pk>/create_tstage/', StructureSetupCreateTournamentStage.as_view(), name='structure_setup.create_tstage'),
    path('structure_setup/<int:pk>/create_tstage/', StageCreateView.as_view(), name='structure_setup.create_tstage'),
    path('structure_setup/<int:pk_tevent>/delete_tstage/<int:pk>/', StageDeleteView.as_view(), name='structure_setup.delete_tstage'),
    path('structure_setup/<int:pk_tevent>/<int:pk_tstage>/create_state', StateCreateView.as_view(), name='structure_setup.create_tstate'),
    path('structure_setup/<int:pk>/tevent_printview', TournamentEventDetail.as_view(), name='structure_setup.tevent_printview'),
    path('structure_setup/<int:pk_tevent>/<int:pk>/tstage_printview', TournamentStageDetail.as_view(), name='structure_setup.tstage_printview'),
    path('structure_setup/<int:pk_tevent>/<int:pk_tstage>/delete_tstate/<int:pk>/', StateDeleteView.as_view(), name='structure_setup.delete_tstate'),
    path('structure_setup/<int:pk_tevent>/<int:pk_tstage>/update_tstate/<int:pk>/', StateUpdateView.as_view(), name='structure_setup.update_tstate'),
    path('structure_setup/<int:pk_tevent>/<int:pk_tstage>/finish_tstate/<int:pk>/', StateFinishView.as_view(), name='structure_setup.finish_tstate'),
    path('structure_setup/<int:pk_tevent>/<int:pk_tstage>/tstate_add_team/<int:pk>/', tstate_add_team, name='structure_setup.tstate_add_team'),
    path('structure_setup/<int:pk_tevent>/<int:pk_tstage>/tstate_delete_team/<int:pk>/', tstate_delete_team, name='structure_setup.tstate_delete_team'),
    path('structure_setup/<int:pk_tevent>/<int:pk_tstage>/update_teamstatsteam/<int:pk>/', TeamStatsUpdateTeamView.as_view(), name='structure_setup.update_teamstatsteam'),
    path('structure_setup/<int:pk_tevent>/<int:pk_tstage>/update_tttransition/<int:pk>/', TTTUpdateView.as_view(), name='structure_setup.update_tttransition'),
    path('structure_setup/<int:pk_tevent>/<int:pk_tstage>/<int:pk_tstate>/create_game/', GameCreateView.as_view(), name='structure_setup.create_game'),
    path('structure_setup/<int:pk_tevent>/<int:pk_tstage>/<int:pk_tstate>/update_teamsetup/', update_teamsetup, name='structure_setup.update_teamsetup'),
    path('structure_setup/<int:pk_tevent>/<int:pk_tstage>/update_game/<int:pk>/', GameUpGameView.as_view(), name='structure_setup.update_game'),
    path('structure_setup/<int:pk_tevent>/<int:pk_tstage>/delete_game/<int:pk>/', GameDeleteView.as_view(), name='structure_setup.delete_game'),
    path('structure_setup/<int:pk_tstate>/games/', games_list, name='games_list'),
    path('structure_setup/<int:pk_tevent>/<int:pk_tstage>/update_game/<int:pk>/<int:from_gameplan>', GameUpGameView.as_view(), name='update_game'),
    path('structure_setup/<int:pk_tevent>/<int:pk_tstage>/update_game_result/<int:pk>/<int:from_gameplan>', GameResultGameView.as_view(), name='update_game_result'),
    path('structure_setup/<int:pk_tevent>/<int:pk_tstage>/update_game_result/<int:pk>/post', postUpdateGameResult, name='post_update_game_result'),
    path('structure_setup/<int:pk_tevent>/<int:pk_tstage>/download_pre_game/<int:pk>', DownloadPreGameView.as_view(), name='download_pre_game'),
    path('structure_setup/<int:pk_tevent>/<int:pk_tstage>/download_pre_game_all/<int:pk>', DownloadPreGameAllView.as_view(), name='download_pre_game_all'),
    

    path('game_plan/', static_views.game_plan, name='game_plan'),
    path('game_plan/delete_all/', static_views.delete_gameplan, name='game_plan.delete_all'),
    path('game_plan/<int:pk_tevent>/<int:pk_tstage>/update_game_result/<int:pk>', GameResultGameView.as_view(), name='update_game_result_from_gameplan'),
    path('results/', static_views.results, name='results'),
    path('results/<int:pk>/', ResultsDetail.as_view(), name='results.detail'),

    path('team_testdata/<int:pk_tevent>/', static_views.create_teamtestdata, name='team_testdata'),
    
    path('livescore/<int:pk_tourn>/', livescore_views.livescore_overview, name='livescore_overview'),
    path('livescore/', livescore_views.livescore_tickeronly, name='livescore_tickeronly'),
    path('livescore/<int:pk_tourn>/display_livestream/<int:pk_court>/', livescore_views.livescore_display_livestream, name='livescore'),
    path('livescore/<int:pk_tourn>/display_big_scoreboard/<int:pk_court>/', livescore_views.livescore_display_big_scoreboard, name='livescore_bigscoreboard'),

]
