from beachhandball_app.models.Player import PlayerStats
from django.urls import path, include
from django.contrib.auth.models import User
from beachhandball_app.models.Game import Game, GameAction
from rest_framework import routers, serializers, viewsets

# Serializers define the API representation.
class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = '__all__'
        depth = 2

class GameRunningSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ('court','act_time','team_st_a', 'team_st_b', 'score_team_a_halftime_1', 'score_team_a_halftime_2', 'score_team_a_penalty', 'score_team_b_halftime_1', 'score_team_b_halftime_2', 'score_team_b_penalty', 'setpoints_team_a', 'setpoints_team_b')
        depth = 0
    

class GameActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameAction
        fields = '__all__'


class PlayerStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerStats
        fields = '__all__'
        depth = 0
