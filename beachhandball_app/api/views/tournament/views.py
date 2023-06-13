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
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

from beachhandball_app import helper
from beachhandball_app.models.Tournaments import Tournament, TournamentEvent, TournamentSettings, TournamentStage, TournamentState, Court, Referee
from beachhandball_app.models.Game import Game
from beachhandball_app.models.Team import TeamStats
from beachhandball_app.models.Player import PlayerStats, Player
from beachhandball_app.api.serializers.tournament import TournamentSerializer, serialize_tournament, serialize_games, serialize_game2, serialize_tournament_full, serialize_tournament_event_stats

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
            ),
            Prefetch("playerstats_set", queryset=PlayerStats.objects.select_related("player__team").filter(is_ranked=True).order_by("-score"), to_attr="player_stats")
        ),
        to_attr="all_tevents"
    )
).filter(season_cup_tournament_id=season_tournament_id).first()

    data = serialize_tournament_event_stats(tourn_data)
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
@cache_page(10)
@renderer_classes([JSONRenderer])
def get_games_info_by_court(request, season_tournament_id, court_id):
    print( 'ENTER get_games_info_by_court season_tournament_id=' + str(season_tournament_id) + ' court_id=' + str(court_id))
    isError = False
    errorCode = 200
    tourn_data = Tournament.objects.prefetch_related(
            Prefetch("game_set", queryset=Game.objects.select_related("tournament", "tournament_event__category", "team_a", "team_b", "team_st_a__team", "team_st_b__team", "ref_a", "ref_b", "tournament_state__tournament_stage", "court").filter(court=court_id).prefetch_related(
                Prefetch("playerstats_set", queryset=PlayerStats.objects.select_related("player__team").filter(is_ranked=False).order_by("-score"), to_attr="player_stats"),
            )
                , to_attr="all_games")
                ).filter(season_cup_tournament_id=season_tournament_id).first()


    t_as_dict = serialize_games(tourn_data.all_games)
    return Response({"isError": isError, "errorCode": errorCode, "message": t_as_dict})


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