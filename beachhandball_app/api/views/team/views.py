# snippets/views.py

import json
from datetime import datetime

from django.db.models.query import Prefetch
from django.http import Http404
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import six
from django.views.decorators.cache import cache_page
from django.db.models import Q

from beachhandball_app.models.Team import Team
from beachhandball_app.api.serializers.game.serializer import GameRunningSerializer, GameRunningSerializer2, PlayerStatsSerializer, TeamSerializer
from beachhandball_app.models.Player import Player, PlayerStats
from beachhandball_app.models.Game import Game, GameAction
from beachhandball_app.api.serializers.game import GameSerializer, GameActionSerializer
from beachhandball_app.api.drf_optimize import OptimizeRelatedModelViewSetMetaclass
from beachhandball_app.models.Tournaments import TournamentEvent
from beachhandball_app.api.serializers.player.serializer import PlayerSerializer

from rest_framework import status
from rest_framework.views import APIView
from rest_framework import authentication, permissions
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, viewsets, renderers
from rest_framework.decorators import action, api_view, authentication_classes, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer


class TeamDetail(APIView):
    """
    Retrieve, update or delete a snippet instance.
    """
    def get_object(self, pk):
        try:
            return Team.objects.get(pk=pk)
        except Team.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = TeamSerializer(snippet)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = TeamSerializer(snippet, data=request.DATA)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        team = self.get_object(pk)
        team.delete()
        return Response(status=status.HTTP_204_NO_CONTENT) 

