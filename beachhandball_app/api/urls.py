from beachhandball_app.api.views.game_report.views import FileUploadView, UploadGameReportViewSet
from beachhandball_app.models.Team import TeamTournamentResult
from django.conf.urls import url
from django.urls import path, include
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView
from .views import login_by_token
from .views.game.views import Login, GameDeleteStatsViewSet, GameViewSet, GameActionViewSet, PlayerStatsSet, PlayerStatsViewSet, RunningGamesDM, ScoutingReportViewSet, RunningGames, TeamViewSet, GameList, StartGameScouting, hello_world, get_pstats_tevent
from .views.tournament.views import get_games_gc_info, get_tournament_info, get_games_info, get_game_info, get_games_info_by_court, get_tournament_struct
from rest_framework import renderers
from rest_framework.authtoken import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'games/upload_report/(?P<pk>\d+)', UploadGameReportViewSet, basename="api_games_upload_report")

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

    path('hello_world/<int:tevent_id>/<int:amount>/', hello_world, name='hello_world'),

    path('tournament/<int:season_tournament_id>/info/', get_tournament_info, name='get_tournament_info'),
    path('tournament/<int:season_tournament_id>/struct/', get_tournament_struct, name='get_tournament_struct'),
    path('tournament/<int:season_tournament_id>/info/games', get_games_info, name='get_games_info'),
    path('tournament/<int:season_tournament_id>/info/games/<int:court_id>', get_games_info_by_court, name='get_games_info_by_court'),
    path('tournament_gc/<int:season_cup_gc_id>/info/games', get_games_gc_info, name='get_games_info'), 

    path('player_stats/<int:pk>/', PlayerStatsSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update'})),
    path('player_stats_by_tevent/<int:tevent_id>/<int:amount>/', get_pstats_tevent, name='get_pstats_tevent'),
    # GAME
    path('gameaction/', GameActionViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('gameaction/<int:pk>/', GameActionViewSet.as_view({'get': 'retrieve'})),

    # TEAM
    path('teams/', TeamViewSet.as_view({'get': 'list'})),
    path('scouting/<int:game_id>/', ScoutingReportViewSet.as_view({'get': 'retrieve', 'post': 'create', 'patch': 'partial_update'})),
    path('scouting/<int:game_id>/start/', StartGameScouting, name='scouting_start'),

    path('', include(router.urls)),
    path('game_report/upload/<int:pk>/', FileUploadView.as_view()),
]