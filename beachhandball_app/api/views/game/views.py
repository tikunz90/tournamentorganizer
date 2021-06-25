# snippets/views.py
from beachhandball_app.api.serializers.player.serializer import PlayerSerializer
import json
from django.db.models import Q

from django.db.models.query import Prefetch
from beachhandball_app.models.Team import Team
from django.http.response import JsonResponse
from rest_framework.views import APIView
from rest_framework import authentication, permissions
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from beachhandball_app.api.serializers.game.serializer import GameRunningSerializer, GameRunningSerializer2, PlayerStatsSerializer, TeamSerializer
from beachhandball_app.models.Player import Player, PlayerStats
from rest_framework import generics, viewsets, renderers
from rest_framework.decorators import action, api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from beachhandball_app.models.Game import Game, GameAction
from beachhandball_app.api.serializers.game import GameSerializer, GameActionSerializer
from django.utils import six
from beachhandball_app.api.drf_optimize import OptimizeRelatedModelViewSetMetaclass


@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def RunningGames(request):
    if request.method == 'GET':
        #games = Game.objects.filter(gamestate='RUNNING').all()
        #serializers = GameRunningSerializer(games,many=True)
        game1 = Game.objects.get(id=62)
        serializers = GameRunningSerializer(game1,read_only=True, many=False)
        data = serializers.data
        data['court'] = game1.court.number
        data['team_st_a'] = game1.team_a.name
        data['team_st_b'] = game1.team_b.name
        game2 = Game.objects.get(id=63)
        serializers = GameRunningSerializer(game2,many=False)
        data2 = serializers.data
        data2['court'] = game2.court.number
        data2['team_st_a'] = game2.team_a.name
        data2['team_st_b'] = game2.team_b.name
        return Response([data, data2])

@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def RunningGamesDM(request):
    if request.method == 'GET':
        #games = Game.objects.filter(gamestate='RUNNING').all()
        #serializers = GameRunningSerializer(games,many=True)
        #all_games = Game.objects.all()
        #for g in all_games:
        #    g.team_a = g.team_st_a.team
        #    g.team_b = g.team_st_b.team
        #    g.act_time = 0
        #    g.save()
        #'court','act_time','team_st_a', 'team_st_b','team_a', 'team_b', 'score_team_a_halftime_1', 'score_team_a_halftime_2', 'score_team_a_penalty', 'score_team_b_halftime_1', 'score_team_b_halftime_2', 'score_team_b_penalty', 'setpoints_team_a', 'setpoints_team_b', 'gamestate', 'gamingstate'
        games = Game.objects.select_related('team_a', 'team_b', 'court').filter(tournament_id=21, gamestate='RUNNING')
        if games.count() == 0:
            return Response([])
        game1 = games.first()
        #serializers = GameRunningSerializer(game1,read_only=True, many=False)
        #data = serializers.data
        data = {}
        data["act_time"] = game1.act_time
        data["score_team_a_halftime_1"] = game1.score_team_a_halftime_1
        data["score_team_a_halftime_2"] = game1.score_team_a_halftime_2
        data["score_team_a_penalty"] = game1.score_team_a_penalty
        data["score_team_b_halftime_1"] = game1.score_team_b_halftime_1
        data["score_team_b_halftime_2"] = game1.score_team_b_halftime_2
        data["score_team_b_penalty"] = game1.score_team_b_penalty
        data["setpoints_team_a"] = game1.setpoints_team_a
        data["setpoints_team_b"] = game1.setpoints_team_b
        data["gamestate"] = game1.gamestate
        data['court'] = game1.court.number
        data['team_st_a'] = game1.team_a.name
        data['team_st_b'] = game1.team_b.name
        data['gamingstate'] = game1.gamingstate
        return Response([data])

@six.add_metaclass(OptimizeRelatedModelViewSetMetaclass)
class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class  = GameSerializer

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        tourn = self.get_object()
        return Response(tourn)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        #data = json.loads(request.data)
        instance.act_time = request.data['act_time']
        instance.score_team_a_halftime_1 = request.data['score_team_a_halftime_1']
        instance.score_team_a_halftime_2 = request.data['score_team_a_halftime_2']
        instance.score_team_a_penalty = request.data['score_team_a_penalty']
        instance.score_team_b_penalty = request.data['score_team_b_penalty']
        instance.score_team_b_halftime_1 = request.data['score_team_b_halftime_1']
        instance.score_team_b_halftime_2 = request.data['score_team_b_halftime_2']
        instance.setpoints_team_a = request.data['setpoints_team_a']
        instance.setpoints_team_b = request.data['setpoints_team_b']
        instance.gamingstate = request.data['gamingstate']
        instance.act_time = request.data['act_time']
        instance.gamestate = request.data['gamestate']
        instance.scouting_state = request.data['scouting_state']
        instance.save(update_fields=['act_time', 'score_team_a_halftime_1', 'score_team_a_halftime_2', 'score_team_a_penalty', 'score_team_b_halftime_1', 'score_team_b_halftime_2', 'score_team_b_penalty', 'setpoints_team_a', 'setpoints_team_b', 'gamestate', 'gamingstate'])
        #serializer = GameRunningSerializer2(instance, data=request.data, partial=True)
        #serializer.is_valid(raise_exception=True)
        #serializer.save()
        return Response(request.data)

class GameReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Game.objects.all()
    serializer_class  = GameSerializer

class GameList(generics.ListAPIView):
    #queryset = Game.objects.all()
    serializer_class = GameSerializer

    def list(self, request, pk_tourn):
        tourn_id = self.kwargs['pk_tourn']
        queryset = Game.objects.select_related('tournament', 'tournament_event__category','tournament_state', 'team_st_a__team', 'team_st_b__team', 'team_a', 'team_b', 'court', 'ref_a', 'ref_b').filter(Q(tournament=tourn_id) & (Q(gamestate='APPENDING') | Q(gamestate='RUNNING')))[:2]
        serializer = GameSerializer(queryset, many=True)
        return Response(serializer.data)

    #def get_queryset(self):
    #    tourn_id = self.kwargs['pk_tourn']
    #    #qq = Game.objects.appending(tourn_id)
    #    qq = Game.objects.select_related('tournament', 'tournament_event__category','tournament_state', 'team_st_a__team', 'team_st_b__team', 'team_a', 'team_b', 'court', 'ref_a', 'ref_b').all()
    #    return qq.filter(tournament=tourn_id, gamestate='APPENDING')
    #    print(qq)
    #    return Game.objects.appending(tourn_id)
    #    return Game.objects.filter(tournament=tourn_id, gamestate='APPENDING')

class PlayerStatsViewSet(viewsets.ModelViewSet):
    queryset = PlayerStats.objects.all()
    serializer_class  = PlayerStatsSerializer

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        tourn = self.get_object()
        return Response(tourn)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = GameRunningSerializer(instance, data=request.data, partial=True)
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

class TeamViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = Team.objects.filter(is_dummy=False).all()
        serializer = TeamSerializer(queryset, many=True)
        return Response(serializer.data)

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

def StartGameScouting(request, game_id):
    if request.method == 'GET':
        response = {}
        response['success'] = False
        response['message'] = ""
        #response['data'] = {}
        if game_id < 0:
            response['message'] = "No game_id passed"
            return JsonResponse(response)
        game = Game.objects.select_related("tournament", "tournament_event__category", "team_st_a__team", "team_st_b__team").prefetch_related(
            Prefetch("team_a__player_set", queryset=Player.objects.all(), to_attr="players"),
            Prefetch("team_b__player_set", queryset=Player.objects.all(), to_attr="players"),
            Prefetch("playerstats_set", queryset=PlayerStats.objects.select_related("tournament_event__category", "player__team", "teamstat").all(), to_attr="pstat")
        ).get(id=game_id)
        players_a = game.team_a.players #[pl for pl in game.team_a.player_set.all()]
        players_b = game.team_b.players #[pl for pl in game.team_b.player_set.all()]
        all_pstats = game.pstat
        pstats_a = [ps for ps in all_pstats if ps.player.team.id == game.team_st_a.team.id]
        pstats_b = [ps for ps in all_pstats if ps.player.team.id == game.team_st_b.team.id]
        pstats_a_new = []
        pstats_b_new = []
        bulk_create_pstats = []
        reload_game = False
        for player in players_a:
            act_stat = None
            for stat in pstats_a:
                if stat.player.id == player.id:
                    act_stat = stat
                    act_stat.season_team_id=player.season_team_id
                    act_stat.season_player_id = player.season_player_id
                    act_stat.season_cup_tournament_id = game.tournament.season_cup_tournament_id
                    act_stat.season_cup_german_championship_id = game.tournament.season_cup_german_championship_id
            if act_stat is None:
                new_stat = PlayerStats(
                    tournament_event= game.tournament_event,
                    game=game,
                    player=player,
                    teamstat=game.team_st_a,
                    season_team_id=player.season_team_id,
                    season_player_id = player.season_player_id,
                    season_cup_tournament_id = game.tournament.season_cup_tournament_id,
                    season_cup_german_championship_id = game.tournament.season_cup_german_championship_id)
                bulk_create_pstats.append(new_stat)
            else:
                pstats_a_new.append(act_stat)
        if len(bulk_create_pstats) > 0:
            reload_game = True
        PlayerStats.objects.bulk_create(bulk_create_pstats)
        bulk_create_pstats = []
        for player in players_b:
            act_stat = None
            for stat in pstats_b:
                if stat.player.id == player.id:
                    act_stat = stat
                    act_stat.season_team_id=player.season_team_id
                    act_stat.season_player_id = player.season_player_id
                    act_stat.season_cup_tournament_id = game.tournament.season_cup_tournament_id
                    act_stat.season_cup_german_championship_id = game.tournament.season_cup_german_championship_id
            if act_stat is None:
                new_stat = PlayerStats(
                    tournament_event= game.tournament_event,
                    game=game,
                    player=player,
                    teamstat=game.team_st_b,
                    season_team_id=player.season_team_id,
                    season_player_id = player.season_player_id,
                    season_cup_tournament_id = game.tournament.season_cup_tournament_id,
                    season_cup_german_championship_id = game.tournament.season_cup_german_championship_id)
                bulk_create_pstats.append(new_stat)
            else:
                pstats_b_new.append(act_stat)
        if len(bulk_create_pstats) > 0:
            reload_game = True
        PlayerStats.objects.bulk_create(bulk_create_pstats)

        if reload_game:
            game_new = Game.objects.prefetch_related(
                Prefetch("playerstats_set", queryset=PlayerStats.objects.all(), to_attr="pstat")
            ).get(id=game_id)
            all_pstats = game_new.pstat
            pstats_a = [ps for ps in all_pstats if ps.player.team.id == game.team_st_a.team.id]
            pstats_b = [ps for ps in all_pstats if ps.player.team.id == game.team_st_b.team.id]
        
        response['game'] = GameSerializer(game).data
        response['players_a'] = PlayerSerializer(players_a, many=True).data
        response['players_b'] = PlayerSerializer(players_b, many=True).data
        
        response['playerstats_a'] = PlayerStatsSerializer(pstats_a, many=True).data
        response['playerstats_b'] = PlayerStatsSerializer(pstats_b, many=True).data
        response['success'] = True
        return JsonResponse(response)
        #games = Game.objects.filter(gamestate='RUNNING').all()
        #serializers = GameRunningSerializer(games,many=True)
        game1 = Game.objects.get(id=62)
        serializers = GameRunningSerializer(game1,read_only=True, many=False)
        data = serializers.data
        data['court'] = game1.court.number
        data['team_st_a'] = game1.team_a.name
        data['team_st_b'] = game1.team_b.name
        game2 = Game.objects.get(id=63)
        serializers = GameRunningSerializer(game2,many=False)
        data2 = serializers.data
        data2['court'] = game2.court.number
        data2['team_st_a'] = game2.team_a.name
        data2['team_st_b'] = game2.team_b.name
        return JsonResponse(json.dump(response))

    if request.method == 'POST':
        #games = Game.objects.filter(gamestate='RUNNING').all()
        #serializers = GameRunningSerializer(games,many=True)
        game1 = Game.objects.get(id=62)
        serializers = GameRunningSerializer(game1,read_only=True, many=False)
        data = serializers.data
        data['court'] = game1.court.number
        data['team_st_a'] = game1.team_a.name
        data['team_st_b'] = game1.team_b.name
        game2 = Game.objects.get(id=63)
        serializers = GameRunningSerializer(game2,many=False)
        data2 = serializers.data
        data2['court'] = game2.court.number
        data2['team_st_a'] = game2.team_a.name
        data2['team_st_b'] = game2.team_b.name
        return Response([data, data2])