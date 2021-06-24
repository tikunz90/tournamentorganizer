from typing import Dict, Any

from beachhandball_app.models.Team import Team
from beachhandball_app.models.Player import PlayerStats
from django.urls import path, include
from django.contrib.auth.models import User
from beachhandball_app.models.Game import Game, GameAction
from rest_framework import routers, serializers, viewsets
from django.utils import six

# Serializers define the API representation.
class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ('id','court','tournament','tournament_event','tournament_state', 'starttime','team_a', 'team_b','team_st_a', 'team_st_b', 'ref_a', 'ref_b', 'gamestate','gamingstate', 'scouting_state')
        depth = 2
        read_only_fields = fields

class GameRunningSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ('court','act_time','team_st_a', 'team_st_b','team_a', 'team_b', 'score_team_a_halftime_1', 'score_team_a_halftime_2', 'score_team_a_penalty', 'score_team_b_halftime_1', 'score_team_b_halftime_2', 'score_team_b_penalty', 'setpoints_team_a', 'setpoints_team_b', 'gamestate', 'gamingstate')
        depth = 0
        #read_only_fields = fields


def serialize_game(game: Game) -> Dict[str, Any]:
    return {
        'id': game.id,
        'starttime': game.starttime.strftime('%H:%M (%d.%m.%Y)'),
        'category': str(game.tournament_event.category),
        'tournament_state': str(game.tournament_state),
        'team_a': str(game.team_a),
        'team_b': str(game.team_b),
        'ref_a': str(game.ref_a),
        'ref_b': str(game.ref_b),
        'score_team_a_halftime_1': game.score_team_a_halftime_1,
        'score_team_a_halftime_2': game.score_team_a_halftime_2,
        'score_team_a_penalty': game.score_team_a_penalty,
        'score_team_b_halftime_1': game.score_team_b_halftime_1,
        'score_team_b_halftime_2': game.score_team_b_halftime_2,
        'score_team_b_penalty': game.score_team_b_penalty,
        'setpoints_team_a': game.setpoints_team_a,
        'setpoints_team_b': game.setpoints_team_b,
        'gamingstate': game.gamingstate,
        'act_time': game.act_time

    }
    

class GameActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameAction
        fields = '__all__'

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ('id', 'name')


class PlayerStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerStats
        fields = '__all__'
        depth = 0
