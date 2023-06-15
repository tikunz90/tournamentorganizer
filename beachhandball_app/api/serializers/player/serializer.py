from typing import Dict, Any

from beachhandball_app.models.Team import Team
from beachhandball_app.models.Player import Player, PlayerStats
from django.urls import path, include
from django.contrib.auth.models import User
from beachhandball_app.models.Game import Game, GameAction
from rest_framework import routers, serializers, viewsets
from django.utils import six

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ('id','tournament_event',
        'team',
        'name',
        'first_name', 
        'number', 
        'birthday' ,
        'position' ,
        'is_active' ,
        'season_team_id',
        'season_player_id',
        'subject_data',
        'gbo_position')
        depth = 0
        read_only_fields = fields

class PlayerStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerStats
        fields = ('id','tournament_event',
        'game',
        'player',
        'teamstat' ,
        'score',
        'kempa_try',
        'kempa_success',
        'spin_try',
        'spin_success',
        'shooter_try',
        'shooter_success',
        'one_try',
        'one_success',
        'suspension',
        'redcard',
        'is_ranked',
        'games_played',
        'goal_keeper_success',
        'block_success'
        )
        depth = 0
        read_only_fields = fields