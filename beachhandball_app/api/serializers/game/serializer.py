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
    

class GameActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameAction
        fields = '__all__'


class PlayerStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerStats
        fields = '__all__'
        depth = 0
