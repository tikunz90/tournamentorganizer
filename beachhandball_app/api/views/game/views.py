# snippets/views.py
from django.http.response import JsonResponse
from rest_framework.views import APIView
from rest_framework import authentication, permissions
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from beachhandball_app.api.serializers.game.serializer import GameRunningSerializer, PlayerStatsSerializer
from beachhandball_app.models.Player import PlayerStats
from rest_framework import generics, viewsets, renderers
from rest_framework.decorators import action, api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from beachhandball_app.models.Game import Game, GameAction
from beachhandball_app.api.serializers.game import GameSerializer, GameActionSerializer


@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def RunningGames(request):
    if request.method == 'GET':
        #games = Game.objects.filter(gamestate='RUNNING').all()
        #serializers = GameRunningSerializer(games,many=True)
        game1 = Game.objects.get(id=60)
        serializers = GameRunningSerializer(game1,many=False)
        data = serializers.data
        data['court'] = game1.court.number
        data['team_st_a'] = game1.team_st_a.team.name
        data['team_st_b'] = game1.team_st_b.team.name
        game2 = Game.objects.get(id=61)
        serializers = GameRunningSerializer(game2,many=False)
        data2 = serializers.data
        data2['court'] = game2.court.number
        data2['team_st_a'] = game2.team_st_a.team.name
        data2['team_st_b'] = game2.team_st_b.team.name
        return Response([data, data2])

class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class  = GameSerializer

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        tourn = self.get_object()
        return Response(tourn)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class GameActionViewSet(viewsets.ModelViewSet):
    queryset = GameAction.objects.all()
    serializer_class  = GameActionSerializer

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        tourn = self.get_object()
        return Response(tourn)


class ScoutingReportViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = Game.objects.all()
        serializer = GameActionSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, game_id=None):
        queryset = Game.objects.all()
        game = get_object_or_404(queryset, pk=game_id)
        serializer = GameSerializer(game)
        ps = PlayerStats.objects.create()
        pss= PlayerStatsSerializer(ps)
        return Response({'game': serializer.data, 'PlayerStat': pss.data})

    def create(self, request, game_id=None):
        return Response(request.data)

    def handle_scouting(self, request, game_id=None):
        pass

    def partial_update(self, request, game_id=None):
        pass