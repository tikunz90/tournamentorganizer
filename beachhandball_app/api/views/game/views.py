# snippets/views.py

import json
from datetime import datetime

from django.contrib.auth import authenticate

from django.db.models.query import Prefetch
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import six
from django.views.decorators.cache import cache_page
from django.db.models import Q
from authentication.models import ScoreBoardUser
from beachhandball_app import helper
from beachhandball_app.api.serializers.tournament.serializer import serialize_court
from beachhandball_app.models.choices import GAMESTATE_CHOICES

from beachhandball_app.models.Team import Team
from beachhandball_app.api.serializers.game.serializer import GameRunningSerializer, GameRunningSerializer2, PlayerStatsSerializer, TeamSerializer
from beachhandball_app.models.Player import Player, PlayerStats
from beachhandball_app.models.Team import Team, TeamStats
from beachhandball_app.models.Game import Game, GameAction
from beachhandball_app.api.serializers.game import GameSerializer, GameEditSerializer, GameActionSerializer
from beachhandball_app.api.drf_optimize import OptimizeRelatedModelViewSetMetaclass
from beachhandball_app.models.Tournaments import TournamentEvent, Court, Referee
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


@api_view(['POST'])
def Login(request):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')

        if username and password:
            # Perform authentication logic here
            user = authenticate(username=username, password=password)
            
            if user is not None:
                # If authentication is successful, return a success response
                sbUser = ScoreBoardUser.objects.get(user=user)
                if sbUser is not None:
                    response = {
                        "isError": False,
                        "errorCode": 200,
                        'message': 'Login successful',
                        'username': username,
                        'court': serialize_court(sbUser.court)
                    }
                else:
                    response = {
                        "isError": True,
                        "errorCode": 200,
                        'message': 'Login failed: ScoreBoardUser not found',
                        'username': username,
                    }
            else:
                response = {
                    "isError": True,
                    "errorCode": 200,
                    'message': 'Login failed',
                    'username': username,
                }
                
            return JsonResponse(response)
        else:
            # Handle missing username or password
            response = {
                "isError": True,
                "errorCode": 200,
                'message': 'Please provide both username and password.',
            }
            return JsonResponse(response, status=400)
    else:
        # Handle non-POST requests
        response = {
            'message': 'Invalid request method. Only POST method is allowed.',
        }
        return JsonResponse(response, status=405)
    
    
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
@cache_page(30)
@renderer_classes([JSONRenderer])
def hello_world(request, tevent_id, amount):
    print( 'ENTER tevent=' + str(tevent_id) + ' amount=' + str(amount))
    
    tevent = TournamentEvent.objects.get(id=tevent_id)

    #orderbyList  = ['starttime','court__name']
    #games = Game.objects.filter(tournament=tevent.tournament).all().order_by(*orderbyList)
    #games_list = [g for g in games]
    #idx = 1
    #for g in games_list:
    #    g.id_counter = idx
    #    g.save()
    #    idx += 1
    
    if amount <= 0:
        global_pstats = PlayerStats.objects.filter(tournament_event=tevent, is_ranked=True).order_by('-score')
    else:
        global_pstats = PlayerStats.objects.filter(tournament_event=tevent, is_ranked=True).order_by('-score')[:amount]

    for ps in global_pstats:
        ps.season_cup_german_championship_id = tevent.season_cup_german_championship_id
        ps.save()
    print('After objects')
    ser = PlayerStatsSerializer(global_pstats, many=True)
    print('After Serializing')
    resp =  Response({"message": "Hello, world!", "pstats": ser.data})
    print('After response')
    return resp

"""Returns running games for DM as JSON response

Returns:
    Response: Contains data as JSON string
"""
@api_view(['GET'])
#@authentication_classes([SessionAuthentication, BasicAuthentication])
#@permission_classes([IsAuthenticated])
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

@api_view(['GET', 'PUT'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def game_update_api(request, pk):
    """
    API endpoint for fetching and updating Game objects
    """
    try:
        # Get the game with all needed related objects in a single query
        game = Game.objects.select_related(
            'tournament',
            'tournament_event', 
            'tournament_event__category',
            'tournament_state',
            'team_st_a', 'team_st_a__team',
            'team_st_b', 'team_st_b__team',
            'team_a', 'team_b',
            'court', 'ref_a', 'ref_b'
        ).get(pk=pk)
    except Game.DoesNotExist:
        return Response({"error": "Game not found"}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        # For GET requests, return the game data and related options
        serializer = GameSerializer(game)
        
        # Get related data for dropdowns
        courts = Court.objects.filter(tournament=game.tournament)
        team_stats = TeamStats.objects.filter(tournamentstate=game.tournament_state)
        referees = Referee.objects.filter(tournament=game.tournament)
        
        # Serialize the related data
        return Response({
            "game": serializer.data,
            "courts": [{"id": c.id, "number": c.number, "name": c.name} for c in courts],
            "team_stats": [{"id": ts.id, "team_id": ts.team_id, "team_name": ts.team.name} for ts in team_stats],
            "referees": [{"id": r.id, "name": f"{r.first_name} {r.name}", "abbreviation": r.abbreviation} for r in referees]
        })
    
    elif request.method == 'PUT':
        # For PUT requests, update the game
        serializer = GameSerializer(game, data=request.data, partial=True)
        if serializer.is_valid():
            # Handle team assignments
            if 'team_st_a' in request.data and game.team_st_a and game.team_st_a.team and not game.team_st_a.team.is_dummy:
                serializer.validated_data['team_a'] = game.team_st_a.team
                
            if 'team_st_b' in request.data and game.team_st_b and game.team_st_b.team and not game.team_st_b.team.is_dummy:
                serializer.validated_data['team_b'] = game.team_st_b.team
            
            # Handle referee subject IDs
            if 'ref_a' in request.data and game.ref_a:
                serializer.validated_data['gbo_ref_a_subject_id'] = game.ref_a.gbo_subject_id
                
            if 'ref_b' in request.data and game.ref_b:
                serializer.validated_data['gbo_ref_b_subject_id'] = game.ref_b.gbo_subject_id
            
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def game_modal_api(request, pk):
    """
    API endpoint for handling Game updates in a modal
    """
    try:
        # Get game with all related objects in a single optimized query
        game = Game.objects.select_related(
            'tournament',
            'tournament_event', 'tournament_event__category',
            'tournament_state', 'tournament_state__tournament_stage',
            'team_st_a', 'team_st_a__team',
            'team_st_b', 'team_st_b__team',
            'team_a', 'team_b',
            'court', 'ref_a', 'ref_b'
        ).get(pk=pk)
    except Game.DoesNotExist:
        return Response({"error": "Game not found"}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        # Get additional data needed for the form
        tournament = game.tournament
        tournament_state = game.tournament_state
        
        # Fetch all necessary related data in bulk queries
        courts = list(Court.objects.filter(tournament=tournament))
        team_stats = list(TeamStats.objects.filter(tournamentstate=tournament_state).select_related('team'))
        referees = list(Referee.objects.filter(tournament=tournament))
        
        # Format response data
        serializer = GameSerializer(game)
        game_data = serializer.data
        
        # Add tournament_stage info for routing purposes
        if game.tournament_state and game.tournament_state.tournament_stage:
            game_data['tournament_stage_id'] = game.tournament_state.tournament_stage.id
        
        response_data = {
            'game': game_data,
            'courts': [{'id': c.id, 'name': c.name, 'number': c.number} for c in courts],
            'team_stats': [{'id': ts.id, 'name': ts.team.name} for ts in team_stats],
            'referees': [{'id': r.id, 'name': f"{r.first_name} {r.name}"} for r in referees],
            'gamestate_choices': [{'value': c[0], 'text': c[1]} for c in GAMESTATE_CHOICES],
            'gamingstate_choices': [{'value': c[0], 'text': c[1]} for c in Game.GAMINGSTATE_CHOICES]
        }
        
        return Response(response_data)
    
    elif request.method == 'PATCH':

        data = request.data.copy()
        starttime = request.data.get('starttime')
        if starttime is not None:
            try:
                # Convert Unix timestamp to datetime
                game.starttime = datetime.fromtimestamp(int(starttime))
                data['starttime'] = datetime.fromtimestamp(int(starttime))
            except Exception as ex:
                return Response({'error': f'Invalid starttime: {ex}'}, status=status.HTTP_400_BAD_REQUEST)

        # Handle court update
        court_id = request.data.get('court')
        if court_id is not None:
            try:
                game.court = Court.objects.get(id=court_id)
            except Court.DoesNotExist:
                return Response({'error': 'Court not found'}, status=status.HTTP_400_BAD_REQUEST)

        # Update the game with the provided data
        serializer = GameEditSerializer(game, data=data, partial=True)
        
        if serializer.is_valid():
            # Auto-assign teams from team_stats if needed
            if ('team_st_a' in request.data and 
                game.team_st_a and 
                game.team_st_a.team and
                not game.team_st_a.team.is_dummy):
                serializer.validated_data['team_a'] = game.team_st_a.team
                
            if ('team_st_b' in request.data and 
                game.team_st_b and 
                game.team_st_b.team and
                not game.team_st_b.team.is_dummy):
                serializer.validated_data['team_b'] = game.team_st_b.team
            
            # Store referee subject IDs
            if 'ref_a' in request.data:
                if request.data['ref_a'] is None:
                    game.ref_a = None
                    serializer.validated_data['gbo_ref_a_subject_id'] = 0
                else:
                    try:
                        ref_a_obj = Referee.objects.get(id=request.data['ref_a'])
                        game.ref_a = ref_a_obj
                        serializer.validated_data['gbo_ref_a_subject_id'] = ref_a_obj.gbo_subject_id
                    except Referee.DoesNotExist:
                        return Response({'error': 'Referee A not found'}, status=status.HTTP_400_BAD_REQUEST)

            if 'ref_b' in request.data:
                if request.data['ref_b'] is None:
                    game.ref_b = None
                    serializer.validated_data['gbo_ref_a_subject_id'] = 0
                else:
                    try:
                        ref_b_obj = Referee.objects.get(id=request.data['ref_b'])
                        game.ref_b = ref_b_obj
                        serializer.validated_data['gbo_ref_b_subject_id'] = ref_b_obj.gbo_subject_id
                    except Referee.DoesNotExist:
                        return Response({'error': 'Referee B not found'}, status=status.HTTP_400_BAD_REQUEST)
            
            game.save(update_fields=['starttime', 'court', 'ref_a', 'ref_b'])
            # Save and return the updated game
            serializer.save()
            return Response(serializer.data)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

@six.add_metaclass(OptimizeRelatedModelViewSetMetaclass)
class GameDeleteStatsViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class  = GameSerializer

    def retrieve(self, request, pk=None):
        game = get_object_or_404(self.queryset, pk=pk)
        result = {'msg':'OK', 'isError': False}
        if not game:
            result['msg'] = "Game not found! id=" + str(pk)
            result['isError'] = True

        local_ps_a = [ps for ps in PlayerStats.objects.filter(tournament_event=game.tournament_event, game=game, player__team=game.team_a, is_ranked=False).all()]
        local_ps_b = [ps for ps in PlayerStats.objects.filter(tournament_event=game.tournament_event, game=game, player__team=game.team_b, is_ranked=False).all()]
        for pstat in local_ps_a:
            pstat.delete()
        for pstat in local_ps_b:
            pstat.delete()
        helper.recalc_global_pstats(game.tournament_event.id)
        return Response(result)

@six.add_metaclass(OptimizeRelatedModelViewSetMetaclass)
class PlayerStatsSet(viewsets.ModelViewSet):
    queryset = PlayerStats.objects.all()
    serializer_class  = PlayerStatsSerializer

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        tourn = self.get_object()
        return Response(tourn)

    def create(self, request):
        pass

    def retrieve(self, request, pk=None):
        pass

    def update(self, request, pk=None):
        instance = self.get_object()
        try:

            #data = json.loads(request.data)
            instance.score = request.data['score']
            instance.spin_success = request.data['spin_success']
            instance.spin_try = request.data['spin_try']
            instance.kempa_success = request.data['kempa_success']
            instance.kempa_try = request.data['kempa_try']
            instance.shooter_success = request.data['shooter_success']
            instance.shooter_try = request.data['shooter_try']
            instance.one_success = request.data['one_success']
            instance.one_try = request.data['one_try']
            instance.goal_keeper_success = request.data['goal_keeper_success']
            instance.block_success = request.data['block_success']
            instance.suspension = request.data['suspension']
            instance.redcard = request.data['redcard']
            instance.sixm_success = request.data['sixmeter_success']
            instance.sixm_try = request.data['sixmeter_try']
            instance.assist_success = request.data['assist_success']
            instance.steal_success = request.data['steal_success']
            instance.turnover_success = request.data['turnover_success']
            instance.save(update_fields=['score', 'spin_success', 'spin_try', 'kempa_success', 'kempa_try', 'shooter_success', 'shooter_try', 'one_success', 'one_try', 'goal_keeper_success', 'block_success', 'suspension', 'redcard', 'sixm_success', 'sixm_try', 'assist_success', 'steal_success', 'turnover_success'])
        except Exception as ex:
            print(ex)
        
        #serializer = GameRunningSerializer2(instance, data=request.data, partial=True)
        #serializer.is_valid(raise_exception=True)
        #serializer.save()
        return Response(request.data)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        #data = json.loads(request.data)
        try:
            instance.score = request.data['score']
            instance.spin_success = request.data['spin_success']
            instance.spin_try = request.data['spin_try']
            instance.kempa_success = request.data['kempa_success']
            instance.kempa_try = request.data['kempa_try']
            instance.shooter_success = request.data['shooter_success']
            instance.shooter_try = request.data['shooter_try']
            instance.one_success = request.data['one_success']
            instance.one_try = request.data['one_try']
            instance.goal_keeper_success = request.data['goal_keeper_success']
            instance.block_success = request.data['block_success']
            instance.suspension = request.data['suspension']
            instance.redcard = request.data['redcard']
            instance.sixmeter_success = request.data['sixmeter_success']
            instance.sixmeter_try = request.data['sixmeter_try']
            instance.assist_success = request.data['assist_success']
            instance.steal_success = request.data['steal_success']
            instance.turnover_success = request.data['turnover_success']
            instance.save(update_fields=['score', 'spin_success', 'spin_try', 'kempa_success', 'kempa_try', 'shooter_success', 'shooter_try', 'one_success', 'one_try', 'goal_keeper_success', 'block_success', 'suspension', 'redcard', 'sixm_success', 'sixm_try', 'assist_success', 'steal_success', 'turnover_success'])
        except Exception as ex:
            print(ex)
        
        #serializer = GameRunningSerializer2(instance, data=request.data, partial=True)
        #serializer.is_valid(raise_exception=True)
        #serializer.save()
        return Response(request.data)

@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
@cache_page(5)
@renderer_classes([JSONRenderer])
def get_pstats_tevent(request, tevent_id, amount):
    print( '[' + str(datetime.now()) + '] ' + 'ENTER tevent=' + str(tevent_id) + ' amount=' + str(amount))
    statusCode = status.HTTP_200_OK
    isError = False
    message = ''
    data = {}
    try:
        tevent = TournamentEvent.objects.select_related('category').get(id=tevent_id)
        data['tevent'] = tevent.name
        data['category_name'] = tevent.category.name
        data['gbo_category_id'] = tevent.category.gbo_category_id
        data['season_tournament_id'] = tevent.season_tournament_id
        data['season_cup_german_championship_id'] = tevent.season_cup_german_championship_id
        data['sub_season_cup_tournament_id'] = tevent.sub_season_cup_tournament_id
        data['season_cup_tournament_id'] = tevent.season_cup_tournament_id
        data['season_tournament_category_id'] = tevent.season_tournament_category_id
        if amount <= 0:
            global_pstats = PlayerStats.objects.filter(tournament_event=tevent, is_ranked=True).order_by('-score')
            message = 'Amount is <= 0'
        else:
            global_pstats = PlayerStats.objects.filter(tournament_event=tevent, is_ranked=True).order_by('-score')[:amount]
        print('After objects')
        ser = PlayerStatsSerializer(global_pstats, many=True)
        data['pstats'] = ser.data
    except Exception as ex:
        print(ex)
        message = str(ex)
        statusCode = status.HTTP_500_INTERNAL_SERVER_ERROR
        isError = True
    
    resp = Response({"isError": isError, "errorCode": statusCode, "message": [data], "info": message})
    print( '[' + str(datetime.now()) + '] ' + 'EXIT tevent=' + str(tevent_id) + ' amount=' + str(amount))
    return resp
class GameReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Game.objects.all()
    serializer_class  = GameSerializer

class GameList(generics.ListAPIView):
    #queryset = Game.objects.all()
    serializer_class = GameSerializer

    def list(self, request, pk_tourn, courtid):
        tourn_id = self.kwargs['pk_tourn']
        queryset = Game.objects.select_related('tournament', 'tournament_event__category','tournament_state', 'team_st_a__team', 'team_st_b__team', 'team_a', 'team_b', 'court', 'ref_a', 'ref_b').filter(Q(tournament=tourn_id) & Q(court=courtid) & (Q(gamestate='APPENDING') | Q(gamestate='RUNNING')))
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

    def create(self, request):
        try:
            datetime_obj = helper.parse_time_from_picker(request.data['gametime'])
            periodString = 'HT1'
            if request.data['period'] == '1.HT':
                periodString = 'HT1'
            elif request.data['period'] == '2.HT':
                periodString = 'HT2'
            elif request.data['period'] == 'P':
                periodString = 'P'
            ga = GameAction(tournament_id=request.data['tournament_id'], gametime=datetime_obj.time(), period=periodString, game_id=request.data['game_id'], player_id=request.data['player_id'], team_id=request.data['team_id'], action=request.data['action'], action_result=request.data['action_result'], score_team_a=request.data['score_team_a'], score_team_b=request.data['score_team_b'], time_min=request.data['time_min'], time_sec=request.data['time_sec'], guid='', active_defending_gk_id=request.data['active_defending_gk_id'])
            ga.save()
            request.data['id'] = ga.id
        except Exception as ex:
            print(ex)
        return Response(request.data)

    @action(detail=False, methods=['delete'], url_path='bulk-delete')
    def bulk_delete(self, request):
        ids = request.data.get('ids', [])
        if not isinstance(ids, list):
            return Response({"error": "ids should be a list."}, status=status.HTTP_400_BAD_REQUEST)
        
        deleted_count, _ = GameAction.objects.filter(id__in=ids).delete()
        return Response({"deleted": deleted_count}, status=status.HTTP_204_NO_CONTENT)
    
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        #data = json.loads(request.data)
        try:
            #instance.timestamp = request.data['timestamp']
            #instance.gametime = request.data['gametime']
            #instance.game = request.data['game']
            #instance.player = request.data['player']
            #instance.team = request.data['team']
            instance.action = request.data['action']
            instance.action_result = request.data['action_result']
            instance.score_team_a = request.data['score_team_a']
            instance.score_team_b = request.data['score_team_b']
            instance.time_min = request.data['time_min']
            instance.time_sec = request.data['time_sec']
            #instance.guid = request.data['guid']
            instance.active_defending_gk_id = request.data['active_defending_gk_id']
            instance.save(update_fields=['action', 'action_result', 'score_team_a', 'score_team_b', 'time_min', 'time_sec'])
        except Exception as ex:
            print(ex)
        
        #serializer = GameRunningSerializer2(instance, data=request.data, partial=True)
        #serializer.is_valid(raise_exception=True)
        #serializer.save()
        return Response(request.data)

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
            Prefetch("playerstats_set", queryset=PlayerStats.objects.select_related("tournament_event__category", "player__team", "teamstat").all(), to_attr="pstat"),
            Prefetch("gameaction_set", queryset=GameAction.objects.all(), to_attr="gameactions")
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

        response['gameactions'] = GameActionSerializer(game.gameactions, many=True).data
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
    