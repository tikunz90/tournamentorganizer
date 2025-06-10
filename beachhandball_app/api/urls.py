from beachhandball_app.api.views.game_report.views import FileUploadView, UploadGameReportViewSet
from beachhandball_app.api.views.team.views import Team2ViewSet
from beachhandball_app.models.Team import TeamTournamentResult
from beachhandball_app.api.views.game.views import game_update_api, game_modal_api, game_update_gametime
from django.conf.urls import url
from django.urls import path, include
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView
from .views import login_by_token
from .views.game.views import Login, games_table_api, GameDeleteStatsViewSet, GameViewSet, GameActionViewSet, PlayerStatsSet, PlayerStatsViewSet, RunningGamesDM, ScoutingReportViewSet, RunningGames, TeamViewSet, GameList, StartGameScouting, hello_world, get_pstats_tevent
from .views.tournament.views import tournament_states_by_event, teams_by_event, set_team_for_teamstat, get_games_gc_info, get_tournament_info, get_games_info, get_game_info, get_games_list_by_court, get_games_info_by_court, get_tournament_struct, get_tournament_struct_light, ttt_detail_api
from rest_framework import renderers
from rest_framework.authtoken import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'games/upload_report/(?P<pk>\d+)', UploadGameReportViewSet, basename="api_games_upload_report")
router.register(r'teams2', Team2ViewSet)

urlpatterns = [
    path('login_by_token/', login_by_token.LoginByToken.as_view()),
    path('login_by_user/', Login),

    # GAME
    path('games/', GameViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('games/<int:pk_tourn>/<int:courtid>/scouting_pending/', GameList.as_view(), name='game_list'),
    path('games/<int:pk>/', GameViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update'})),
    path('games/<int:pk>/delete_stats', GameDeleteStatsViewSet.as_view({'get': 'retrieve',}), name='api_game_delete_stats'),
    path('games/running/', RunningGames, name='get_running_games'),
    path('games/running/dm/', RunningGamesDM, name='get_running_games_dm'),
    path('games/<int:game_id>/info/', get_game_info, name='get_game_info'),
    path('games/bycourt/<int:court_id>/', get_games_list_by_court, name='get_games_list_by_court'),
    path('games/<int:pk>/modal/', game_modal_api, name='game_modal_api'),
    path('games/<int:pk>/update/', game_update_api, name='game_update_api'),
    path('games/<int:pk>/update_game_time/', game_update_gametime, name='game_update_gametime_api'),
    path('games/table/', games_table_api, name='games_table_api'),

    path('hello_world/<int:tevent_id>/<int:amount>/', hello_world, name='hello_world'),

    path('tournament/<int:season_tournament_id>/info/', get_tournament_info, name='get_tournament_info'),
    path('tournament/<int:season_tournament_id>/struct/', get_tournament_struct, name='get_tournament_struct'),
    path('tournament/<int:season_tournament_id>/struct_light/', get_tournament_struct_light, name='get_tournament_struct_light'),
    path('tournament/<int:season_tournament_id>/info/games', get_games_info, name='get_games_info'),
    path('tournament/<int:season_tournament_id>/info/games/<int:court_id>', get_games_info_by_court, name='get_games_info_by_court'),
    path('tournament_gc/<int:season_cup_gc_id>/info/games', get_games_gc_info, name='get_games_info'),
    path('tournament/tournamentstates/', tournament_states_by_event, name='tournament_states_by_event'),
    path('tournament/ttt/<int:pk>/', ttt_detail_api, name='ttt-detail-api'),

    path('player_stats/<int:pk>/', PlayerStatsSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update'})),
    path('player_stats_by_tevent/<int:tevent_id>/<int:amount>/', get_pstats_tevent, name='get_pstats_tevent'),
    # GAME
    path('gameaction/', GameActionViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('gameaction/<int:pk>/', GameActionViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})),
    path('gameaction/bulk-delete/', GameActionViewSet.as_view({'delete': 'bulk_delete'})),

    # TEAM
    path('teams/', TeamViewSet.as_view({'get': 'list'})),
    path('scouting/<int:game_id>/', ScoutingReportViewSet.as_view({'get': 'retrieve', 'post': 'create', 'patch': 'partial_update'})),
    path('scouting/<int:game_id>/start/', StartGameScouting, name='scouting_start'),
    path('teams/by_event/<int:tevent_id>/', teams_by_event, name='teams_by_event'),
    path('teamstats/<int:tstat_id>/set_team/', set_team_for_teamstat, name='set_team_for_teamstat'),

    path('', include(router.urls)),
    path('game_report/upload/<int:pk>/', FileUploadView.as_view()),
]