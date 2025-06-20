from django.views.decorators.cache import cache_page
from django.db.models.query import Prefetch
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.core import serializers

from rest_framework import status
from rest_framework.views import APIView
from rest_framework import authentication, permissions
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, viewsets, renderers
from rest_framework.decorators import action, api_view, authentication_classes, permission_classes, renderer_classes
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

from beachhandball_app import helper
from beachhandball_app.models.Tournaments import Tournament, TournamentEvent, TournamentSettings, TournamentStage, TournamentState, Court, Referee, TournamentTeamTransition
from beachhandball_app.models.Game import Game
from beachhandball_app.models.Team import TeamStats, Team
from beachhandball_app.models.Player import PlayerStats, Player
from beachhandball_app.api.serializers.tournament import TournamentSerializer, TournamentTeamTransitionSerializer, serialize_tournament, serialize_games, serialize_game2, serialize_tournament_full, serialize_tournament_event_stats, serialize_games_with_depth

@api_view(['GET'])
#@authentication_classes([SessionAuthentication, BasicAuthentication])
#@permission_classes([IsAuthenticated])
@cache_page(1)
@renderer_classes([JSONRenderer])
def get_tournament_info(request, season_tournament_id):
    print( 'ENTER get_tournament_info season_tournament_id=' + str(season_tournament_id))
    isError = False
    errorCode = 200
    tourn_data = Tournament.objects.prefetch_related(
    Prefetch(
        "tournamentevent_set",
        queryset=TournamentEvent.objects.select_related("tournament", "category").prefetch_related(
            Prefetch(
                "tournamentstage_set",
                queryset=TournamentStage.objects.select_related("tournament_event__category").prefetch_related(
                    Prefetch(
                        "tournamentstate_set",
                        queryset=TournamentState.objects.select_related("tournament_event__category", "tournament_stage").prefetch_related(
                            Prefetch(
                                "teamstats_set",
                                queryset=TeamStats.objects.select_related("team").order_by("rank"),
                                to_attr="all_team_stats"
                            )
                        ),
                        to_attr="all_tstates"
                    )
                ),
                to_attr="all_tstages"
            )
        ),
        to_attr="all_tevents"
    )
).filter(season_cup_tournament_id=season_tournament_id).first()

    #global_pstats = PlayerStats.objects.filter(tournament_event=tevent, is_ranked=True).order_by('-score')[:amount]
    #print('After objects')
    #ser = PlayerStatsSerializer(global_pstats, many=True)
    
    #tSerializer = TournamentSerializer(t)
    t_as_dict = serialize_tournament(tourn_data)
    #tevent = TournamentEvent.objects.get(id=tevent_id)
    #
    #if amount <= 0:
    #    global_pstats = PlayerStats.objects.filter(tournament_event=tevent, is_ranked=True).order_by('-score')
    #else:
    #    global_pstats = PlayerStats.objects.filter(tournament_event=tevent, is_ranked=True).order_by('-score')[:amount]
    #print('After objects')
    #ser = PlayerStatsSerializer(global_pstats, many=True)
    #print('After Serializing')
    #resp =  Response({"message": "Hello, world!", "pstats": ser.data})
    #print('After response')
    return Response({"isError": isError, "errorCode": errorCode, "message": t_as_dict})


@api_view(['GET'])
#@authentication_classes([SessionAuthentication, BasicAuthentication])
#@permission_classes([IsAuthenticated])
@cache_page(1)
@renderer_classes([JSONRenderer])
def get_tournament_struct(request, season_tournament_id):
    print( 'ENTER get_tournament_info season_tournament_id=' + str(season_tournament_id))
    isError = False
    errorCode = 200
    """ tourn_data = Tournament.objects.prefetch_related(
    Prefetch(
        "tournamentevent_set",
        queryset=TournamentEvent.objects.select_related("tournament", "category").prefetch_related(
            Prefetch(
                "tournamentstage_set",
                queryset=TournamentStage.objects.select_related("tournament_event__category").prefetch_related(
                    Prefetch(
                        "tournamentstate_set",
                        queryset=TournamentState.objects.select_related("tournament_event__category", "tournament_stage").prefetch_related(
                            Prefetch(
                                "teamstats_set",
                                queryset=TeamStats.objects.select_related("team").order_by("rank"),
                                to_attr="all_team_stats"
                            )
                        ),
                        to_attr="all_tstates"
                    )
                ),
                to_attr="all_tstages"
            ),
            Prefetch("playerstats_set", queryset=PlayerStats.objects.select_related("player__team").filter(is_ranked=True).order_by("-score"), to_attr="player_stats")
        ),
        to_attr="all_tevents"
    )
).filter(season_cup_tournament_id=season_tournament_id).first() """
    tourn_data = Tournament.objects.filter(season_cup_tournament_id=season_tournament_id).first()
    print('Query Done')
    #data = serialize_tournament_full(tourn_data)
    data = helper.get_tournament_info_json(tourn_data)
    print('Serialize Done')
    #global_pstats = PlayerStats.objects.filter(tournament_event=tevent, is_ranked=True).order_by('-score')[:amount]
    #print('After objects')
    #ser = PlayerStatsSerializer(global_pstats, many=True)
    #tSerializer = TournamentSerializer(t)
    #t_as_dict = serialize_tournament_full(tourn_data)
    #tevent = TournamentEvent.objects.get(id=tevent_id)
    #
    #if amount <= 0:
    #    global_pstats = PlayerStats.objects.filter(tournament_event=tevent, is_ranked=True).order_by('-score')
    #else:
    #    global_pstats = PlayerStats.objects.filter(tournament_event=tevent, is_ranked=True).order_by('-score')[:amount]
    #print('After objects')
    #ser = PlayerStatsSerializer(global_pstats, many=True)
    #print('After Serializing')
    #resp =  Response({"message": "Hello, world!", "pstats": ser.data})
    #print('After response')
    return Response({"isError": isError, "errorCode": errorCode, "message": data})


@api_view(['GET'])
#@authentication_classes([SessionAuthentication, BasicAuthentication])
#@permission_classes([IsAuthenticated])
@cache_page(1)
@renderer_classes([JSONRenderer])
def get_tournament_struct_light(request, season_tournament_id):
    print( 'ENTER get_tournament_info_light season_tournament_id=' + str(season_tournament_id))
    isError = False
    errorCode = 200
    try:

        tourn_data = Tournament.objects.filter(season_cup_tournament_id=season_tournament_id).first()
        data = helper.get_tournament_info_light_json(tourn_data)
    except Exception as ex:
        errorCode = 401
        data = repr(ex)
    return Response({"isError": isError, "errorCode": errorCode, "message": data})

@api_view(['GET'])
#@authentication_classes([SessionAuthentication, BasicAuthentication])
#@permission_classes([IsAuthenticated])
@cache_page(10)
@renderer_classes([JSONRenderer])
def get_games_info(request, season_tournament_id):
    print( 'ENTER get_games_info season_tournament_id=' + str(season_tournament_id))
    isError = False
    errorCode = 200
    tourn_data = Tournament.objects.prefetch_related(
            Prefetch("game_set", queryset=Game.objects.select_related("tournament", "tournament_event__category", "team_a", "team_b", "team_st_a__team", "team_st_b__team", "ref_a", "ref_b", "tournament_state__tournament_stage", "court").prefetch_related(
                Prefetch("playerstats_set", queryset=PlayerStats.objects.select_related("player__team").filter(is_ranked=False).order_by("-score"), to_attr="player_stats"),
            )
                , to_attr="all_games")
                ).filter(season_cup_tournament_id=season_tournament_id).first()


    t_as_dict = serialize_games(tourn_data.all_games)
    return Response({"isError": isError, "errorCode": errorCode, "message": t_as_dict})


@api_view(['GET'])
#@authentication_classes([SessionAuthentication, BasicAuthentication])
#@permission_classes([IsAuthenticated])
@cache_page(3)
@renderer_classes([JSONRenderer])
def get_games_info_by_court(request, season_tournament_id, court_id):
    print( 'ENTER get_games_info_by_court season_tournament_id=' + str(season_tournament_id) + ' court_id=' + str(court_id))
    isError = False
    errorCode = 200

    fetch_depth = request.query_params.get('depth', 'full').lower()

    # Base query to filter games by court
    games_query = Game.objects.filter(court_id=court_id)

    # Apply common select_related for all depth levels
    common_select = [
        "tournament",
        "tournament_event",
        "tournament_event__category",
        "tournament_state",
        "team_a", 
        "team_b", 
        "court"
    ]

    if fetch_depth == 'minimal':
        # Minimal data - just essential fields
        games = games_query.select_related(
            *common_select,
            "team_st_a",
            "team_st_b",
            "team_st_a__team",
            "team_st_b__team"
        )
    elif fetch_depth == 'medium':
        # Medium data - include team stats and refs, but no player data
        games = games_query.select_related(
            *common_select,
            "team_st_a",
            "team_st_b", 
            "team_st_a__team", 
            "team_st_b__team",
            "ref_a", 
            "ref_b", 
            "tournament_state__tournament_stage"
        )
    else:  # full depth by default
        # Full data - include all related data including player stats
        games = games_query.select_related(
            *common_select,
            "team_st_a",
            "team_st_b", 
            "team_st_a__team", 
            "team_st_b__team",
            "ref_a", 
            "ref_b", 
            "tournament_state__tournament_stage"
        ).prefetch_related(
            # Prefetch player stats with player and team relationships
            Prefetch(
                "playerstats_set", 
                queryset=PlayerStats.objects.select_related(
                    "player", 
                    "player__team"
                ).filter(is_ranked=False).order_by("-score"), 
                to_attr="player_stats"
            ),
            # Prefetch team_a players
            Prefetch(
                "team_a__player_set",
                queryset=Player.objects.select_related("team"),
                to_attr="team_a_players"
            ),
            # Prefetch team_b players
            Prefetch(
                "team_b__player_set",
                queryset=Player.objects.select_related("team"),
                to_attr="team_b_players"
            )
        )


    # Include additional metrics in response
    game_count = games.count()
    
    # Convert to dictionary for the response
    games_data = serialize_games_with_depth(games, fetch_depth)
    
    return Response({
        "isError": isError, 
        "errorCode": errorCode, 
        "message": games_data,
        "metadata": {
            "fetch_depth": fetch_depth,
            "game_count": game_count,
            "court_id": court_id,
            "season_tournament_id": season_tournament_id
        }
    })


@api_view(['GET'])
#@authentication_classes([SessionAuthentication, BasicAuthentication])
#@permission_classes([IsAuthenticated])
@cache_page(10)
@renderer_classes([JSONRenderer])
def get_game_info(request, game_id):
    print( 'ENTER get_game_info game_id=' + str(game_id))
    isError = False
    errorCode = 200
    game = get_object_or_404(Game.objects.select_related("tournament", "tournament_event__category", "team_a", "team_b", "team_st_a__team", "team_st_b__team", "ref_a", "ref_b", "tournament_state__tournament_stage", "court").prefetch_related(
            "team_a__player_set",
            "team_b__player_set"
        ), id=game_id)
    
    t_as_dict = serialize_game2(game)
    return Response({"isError": isError, "errorCode": errorCode, "message": t_as_dict})

@api_view(['GET'])
#@authentication_classes([SessionAuthentication, BasicAuthentication])
#@permission_classes([IsAuthenticated])
@cache_page(10)
@renderer_classes([JSONRenderer])
def get_games_list_by_court(request, court_id):
    print( 'ENTER get_games_list_by_court ' + str(court_id))
    isError = False
    errorCode = 200
    
    games = Game.objects.filter(court_id=court_id).select_related(
        "tournament",
        "tournament_event__category",
        "team_a",
        "team_b",
        "team_st_a__team",
        "team_st_b__team",
        "ref_a",
        "ref_b",
        "tournament_state__tournament_stage",
        "court"
    )


    t_as_dict = serialize_games(games)
    return Response({"isError": isError, "errorCode": errorCode, "message": t_as_dict})

@api_view(['GET'])
#@authentication_classes([SessionAuthentication, BasicAuthentication])
#@permission_classes([IsAuthenticated])
@cache_page(1)
@renderer_classes([JSONRenderer])
def get_games_gc_info(request, season_cup_gc_id):
    print( 'ENTER get_tournament_info season_cup_gc_id=' + str(season_cup_gc_id))
    isError = False
    errorCode = 200
    tourn_data = Tournament.objects.prefetch_related(
            Prefetch("game_set", queryset=Game.objects.select_related("tournament", "tournament_event__category", "team_a", "team_b", "team_st_a__team", "team_st_b__team", "ref_a", "ref_b", "tournament_state__tournament_stage", "court").prefetch_related(
                Prefetch("playerstats_set", queryset=PlayerStats.objects.select_related("player__team").filter(is_ranked=False).order_by("-score"), to_attr="player_stats"),
            )
                , to_attr="all_games")
                ).filter(season_cup_german_championship_id=season_cup_gc_id).first()


    t_as_dict = serialize_games(tourn_data.all_games)
    return Response({"isError": isError, "errorCode": errorCode, "message": t_as_dict})

@api_view(['GET'])
#@authentication_classes([SessionAuthentication, BasicAuthentication])
#@permission_classes([IsAuthenticated])
@cache_page(1)
@renderer_classes([JSONRenderer])
def teams_by_event(request, tevent_id):
    teams = Team.objects.filter(tournament_event_id=tevent_id, is_dummy=False)
    return JsonResponse({'teams': [{'id': t.id, 'name': t.name} for t in teams]})

from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def set_team_for_teamstat(request, tstat_id):
    if request.method == 'POST':
        team_id = request.POST.get('team_id')
        tstat = TeamStats.objects.get(id=tstat_id)
        tstat.name_table = Team.objects.get(id=team_id).name
        tstat.team_id = team_id
        tstat.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tournament_states_by_event(request):
    tevent_id = request.GET.get('tournament_event')
    if not tevent_id:
        return Response([], status=400)
    states = TournamentState.objects.filter(tournament_event_id=tevent_id)
    data = [
        {'id': s.id, 'name': s.name, 'abbreviation': s.abbreviation}
        for s in states
    ]
    return Response(data)

@api_view(['GET', 'PATCH'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
@ensure_csrf_cookie
def ttt_detail_api(request, pk):
    try:
        ttt = TournamentTeamTransition.objects.get(pk=pk)
    except TournamentTeamTransition.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = TournamentTeamTransitionSerializer(ttt)
        return Response(serializer.data)

    if request.method == 'PATCH':
        data = request.data
        data['tournament_event'] = ttt.tournament_event.id

        serializer = TournamentTeamTransitionSerializer(ttt, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)