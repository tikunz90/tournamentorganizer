from beachhandball_app.models.Team import TeamTournamentResult
from django.conf.urls import url
from django.urls import path, include
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView
from .views import login_by_token
from .views.game.views import GameViewSet, GameActionViewSet, ScoutingReportViewSet, RunningGames, TeamViewSet, GameList, StartGameScouting

from rest_framework import renderers
from rest_framework.authtoken import views

urlpatterns = [
    path('login_by_token/', login_by_token.LoginByToken.as_view()),

    # GAME
    path('games/', GameViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('games/<int:pk_tourn>/scouting_pending/', GameList.as_view(), name='game_list'),
    path('games/<int:pk>/', GameViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update'})),
    path('games/running/', RunningGames, name='get_running_games'),

    # GAME
    path('gameaction/', GameActionViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('gameaction/<int:pk>/', GameActionViewSet.as_view({'get': 'retrieve'})),

    # TEAM
    path('teams/', TeamViewSet.as_view({'get': 'list'})),
    path('scouting/<int:game_id>/', ScoutingReportViewSet.as_view({'get': 'retrieve', 'post': 'create', 'patch': 'partial_update'})),
    path('scouting/<int:game_id>/start/', StartGameScouting, name='scouting_start'),
]