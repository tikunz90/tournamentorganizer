import time
from typing import Dict, Any

from rest_framework import routers, serializers, viewsets
from beachhandball_app.models.Game import Game

from beachhandball_app.models.Tournaments import Court, Tournament, TournamentEvent, TournamentStage, TournamentState, TournamentTeamTransition
from beachhandball_app.models.General import TournamentCategory
from beachhandball_app.models.Team import Team, TeamStats
from beachhandball_app.models.Player import Player, PlayerStats

class TournamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournament
        fields = ('id', 'name', 'created_at', 'is_active', 'last_sync_at', 'season_tournament_id', 'season_cup_tournament_id')
        depth = 0

def serialize_tournament_full(tournament: Tournament) -> Dict[str, Any]:
    return {
        'id': tournament.id,
        'created_at': tournament.created_at,#tournament.starttime.strftime('%H:%M (%d.%m.%Y)'),
        'is_active': tournament.is_active,
        'last_sync_at': tournament.last_sync_at,
        'season_tournament_id': tournament.season_tournament_id,
        'season_cup_tournament_id': tournament.season_cup_tournament_id,
        'events': [serialize_tournament_event_and_games(event, tournament.all_games) for event in tournament.all_tevents]
    }

def serialize_tournament_multi_full(tournament: Tournament) -> Dict[str, Any]:
    return {
        'id': tournament.id,
        'created_at': tournament.created_at,#tournament.starttime.strftime('%H:%M (%d.%m.%Y)'),
        'is_active': tournament.is_active,
        'last_sync_at': tournament.last_sync_at,
        'season_tournament_id': tournament.season_tournament_id,
        'season_cup_tournament_id': tournament.season_cup_tournament_id,
        'events': [serialize_tournament_event_and_games(event, tournament.all_games) for event in tournament.all_tevents]
    }

def serialize_tournament_light(tournament: Tournament) -> Dict[str, Any]:
    return {
        'id': tournament.id,
        'created_at': tournament.created_at,#tournament.starttime.strftime('%H:%M (%d.%m.%Y)'),
        'is_active': tournament.is_active,
        'last_sync_at': tournament.last_sync_at,
        'season_tournament_id': tournament.season_tournament_id,
        'season_cup_tournament_id': tournament.season_cup_tournament_id,
        'events': [serialize_tournament_event_light(event) for event in tournament.all_tevents]
    }

def serialize_tournament_event_and_games(tournamentEvent: TournamentEvent, games) -> Dict[str, Any]:
    data = {
        'id': tournamentEvent.id,
        'tournamentId': tournamentEvent.tournament.id,
        'name': tournamentEvent.name,
        'category': serialize_tournament_category(tournamentEvent.category),
        'stages': [serialize_tournament_stage(stage, [g for g in games if g.tournament_event_id == tournamentEvent.id]) for stage in tournamentEvent.all_tstages]
    }
    if hasattr(tournamentEvent, 'top10_player_stats_offense'):
        data['top10_player_stats_offense'] = [serialize_playerstat(stat) for stat in tournamentEvent.top10_player_stats_offense[:10]]
    if hasattr(tournamentEvent, 'top10_player_stats_defense'):
        data['top10_player_stats_defense'] = [serialize_playerstat(stat) for stat in tournamentEvent.top10_player_stats_defense[:10]]
    if hasattr(tournamentEvent, 'top10_player_stats_gk'):
        data['top10_player_stats_gk'] = [serialize_playerstat(stat) for stat in tournamentEvent.top10_player_stats_gk[:10]]
    return data

def serialize_tournament_event_light(tournamentEvent: TournamentEvent) -> Dict[str, Any]:
    data = {
        'id': tournamentEvent.id,
        'name': tournamentEvent.name,
        'category': serialize_tournament_category(tournamentEvent.category),
        'stages': [serialize_tournament_stage_light(stage, []) for stage in tournamentEvent.all_tstages]
    }
    if hasattr(tournamentEvent, 'top10_player_stats_offense'):
        data['top10_player_stats_offense'] = [serialize_playerstat(stat) for stat in tournamentEvent.top10_player_stats_offense[:5]]
    if hasattr(tournamentEvent, 'top10_player_stats_defense'):
        data['top10_player_stats_defense'] = [serialize_playerstat(stat) for stat in tournamentEvent.top10_player_stats_defense[:5]]
    if hasattr(tournamentEvent, 'top10_player_stats_gk'):
        data['top10_player_stats_gk'] = [serialize_playerstat(stat) for stat in tournamentEvent.top10_player_stats_gk[:5]]
    return data

def serialize_tournament_event_stats(tournamentEvent: TournamentEvent) -> Dict[str, Any]:
    data = {
        'id': tournamentEvent.id,
        'name': tournamentEvent.name,
        'player_stats': tournamentEvent.player_stats,
        #'category': serialize_tournament_category(tournamentEvent.category),
        #'stages': [serialize_tournament_stage(stage, [g for g in games if g.tournament_event_id == tournamentEvent.id]) for stage in tournamentEvent.all_tstages]
    }
    if hasattr(tournamentEvent, 'top10_player_stats_offense'):
        data['top10_player_stats_offense'] = [serialize_playerstat(stat) for stat in tournamentEvent.top10_player_stats_offense[:10]]
    if hasattr(tournamentEvent, 'top10_player_stats_defense'):
        data['top10_player_stats_defense'] = [serialize_playerstat(stat) for stat in tournamentEvent.top10_player_stats_defense[:10]]
    if hasattr(tournamentEvent, 'top10_player_stats_gk'):
        data['top10_player_stats_gk'] = [serialize_playerstat(stat) for stat in tournamentEvent.top10_player_stats_gk[:10]]
    return data

def serialize_tournament_category(category: TournamentCategory) -> Dict[str, Any]:
    return {
        'id': category.id,
        'name': category.name,
        'category': category.category,
        'classification': category.classification,
        'gbo_category_id': category.gbo_category_id,
        'season_tournament_category_id': category.season_tournament_category_id,
    }

def serialize_tournament_stage(stage: TournamentStage, games) -> Dict[str, Any]:
    return {
        'id': stage.id,
        'name': stage.name,
        'tournament_stage': stage.tournament_stage,
        'order': stage.order,
        'states': [serialize_tournament_state_and_games(state, games) for state in stage.all_tstates]
    }

def serialize_tournament_stage_light(stage: TournamentStage, games) -> Dict[str, Any]:
    return {
        'id': stage.id,
        'name': stage.name,
        'tournament_stage': stage.tournament_stage,
        'order': stage.order,
        'states': [serialize_tournament_state_light(state) for state in stage.all_tstates]
    }

def serialize_tournament_state_and_games(state: TournamentState, games) -> Dict[str, Any]:
    return {
        'id': state.id,
        'abbreviation': state.abbreviation,
        'hierarchy': state.hierarchy,
        'max_number_teams': state.max_number_teams,
        'min_number_teams': state.min_number_teams,
        'is_final': state.is_final,
        'is_finished': state.is_finished,
        'games' : [serialize_game(g) for g in games if g.tournament_state_id == state.id],
        'ranking': [serialize_teamstat(stat) for stat in state.all_team_stats]
    }

def serialize_tournament_state_light(state: TournamentState) -> Dict[str, Any]:
    return {
        'id': state.id,
        'abbreviation': state.abbreviation,
        'hierarchy': state.hierarchy,
        'max_number_teams': state.max_number_teams,
        'min_number_teams': state.min_number_teams,
        'is_final': state.is_final,
        'is_finished': state.is_finished,
        'games' : [],
        'ranking': [serialize_teamstat(stat) for stat in state.all_team_stats]
    }

def serialize_game(game: Game) -> Dict[str, Any]:
    ps_a = []
    ps_b = []
    if hasattr(game, 'player_stats'):
        ps_a = [serialize_playerstat(ps) for ps in game.player_stats if ps.player.team_id == game.team_a.id]
        ps_b = [serialize_playerstat(ps) for ps in game.player_stats if ps.player.team_id == game.team_b.id]

    return {
        'id': game.id,
        'team_a': serialize_team(game.team_a),
        'team_b': serialize_team(game.team_b),
        'team_st_a': serialize_teamstat(game.team_st_a),
        'team_st_b': serialize_teamstat(game.team_st_b),
        'starttime': time.mktime(game.starttime.timetuple()),
        'court': serialize_court_wo_tourns(game.court),
        'duration_of_halftime': game.duration_of_halftime,
        'score_team_a_halftime_1': game.score_team_a_halftime_1,
        'score_team_a_halftime_2': game.score_team_a_halftime_2,
        'score_team_a_penalty': game.score_team_a_penalty,
        'score_team_b_halftime_1': game.score_team_b_halftime_1,
        'score_team_b_halftime_2': game.score_team_b_halftime_2,
        'score_team_b_penalty': game.score_team_b_penalty,
        'gamestate': game.gamestate,
        'gamingstate': game.gamingstate,
        'player_stats_team_a': ps_a,
        'player_stats_team_b': ps_b,
        'tournament': serialize_tournament(game.tournament),
        'tournament_event': serialize_tournament_event(game.tournament_event),
        'tournament_state': serialize_tournament_state(game.tournament_state),
    }

def serialize_game2(game: Game) -> Dict[str, Any]:
    return {
        'id': game.id,
        'team_a': serialize_team(game.team_a, True),
        'team_b': serialize_team(game.team_b, True),
        'team_st_a': serialize_teamstat(game.team_st_a),
        'team_st_b': serialize_teamstat(game.team_st_b),
        'starttime': time.mktime(game.starttime.timetuple()),
        'court': serialize_court(game.court),
        'duration_of_halftime': game.duration_of_halftime,
        'score_team_a_halftime_1': game.score_team_a_halftime_1,
        'score_team_a_halftime_2': game.score_team_a_halftime_2,
        'score_team_a_penalty': game.score_team_a_penalty,
        'score_team_b_halftime_1': game.score_team_b_halftime_1,
        'score_team_b_halftime_2': game.score_team_b_halftime_2,
        'score_team_b_penalty': game.score_team_b_penalty,
        'gamestate': game.gamestate,
        'gamingstate': game.gamingstate,
        'tournament': serialize_tournament(game.tournament),
        'tournament_event': serialize_tournament_event(game.tournament_event),
        'tournament_state': serialize_tournament_state(game.tournament_state),
    }

def serialize_game_no_players(game: Game) -> Dict[str, Any]:
    ps_a = []
    ps_b = []
    if hasattr(game, 'player_stats'):
        ps_a = [serialize_playerstat(ps) for ps in game.player_stats if ps.player.team_id == game.team_a.id]
        ps_b = [serialize_playerstat(ps) for ps in game.player_stats if ps.player.team_id == game.team_b.id]

    return {
        'id': game.id,
        'team_a': serialize_team(game.team_a),
        'team_b': serialize_team(game.team_b),
        'team_st_a': serialize_teamstat(game.team_st_a),
        'team_st_b': serialize_teamstat(game.team_st_b),
        'starttime': time.mktime(game.starttime.timetuple()),
        'court': serialize_court_wo_tourns(game.court),
        'duration_of_halftime': game.duration_of_halftime,
        'score_team_a_halftime_1': game.score_team_a_halftime_1,
        'score_team_a_halftime_2': game.score_team_a_halftime_2,
        'score_team_a_penalty': game.score_team_a_penalty,
        'score_team_b_halftime_1': game.score_team_b_halftime_1,
        'score_team_b_halftime_2': game.score_team_b_halftime_2,
        'score_team_b_penalty': game.score_team_b_penalty,
        'gamestate': game.gamestate,
        'gamingstate': game.gamingstate,
        'player_stats_team_a': ps_a,
        'player_stats_team_b': ps_b,
        'tournament': serialize_tournament(game.tournament),
        'tournament_event': serialize_tournament_event(game.tournament_event),
        'tournament_state': serialize_tournament_state(game.tournament_state),
    }

def serialize_games_with_depth(games, depth='full'):
    """
    Serialize games with different depth levels to optimize database queries
    """
    if depth == 'minimal':
        return {
            'games': [
                {
                    'id': game.id,
                    'starttime': time.mktime(game.starttime.timetuple()) if game.starttime else None,
                    'gamestate': game.gamestate,
                    'gamingstate': game.gamingstate,
                    'duration_of_halftime': game.duration_of_halftime,
                    'team_a': {
                        'id': game.team_a.id if game.team_a else None,
                        'name': game.team_a.name if game.team_a else 'Unknown',
                        'abbreviation': game.team_a.abbreviation if game.team_a else '',
                        'is_dummy': game.team_a.is_dummy if game.team_a else False,
                        'gbo_team': game.team_a.gbo_team if game.team_a else 0,
                        'season_team_id': game.team_a.season_team_id if game.team_a else -1,
                        'season_team_cup_tournament_ranking_id': game.team_a.season_team_cup_tournament_ranking_id if game.team_a else -1,
                        'season_team_cup_championship_ranking_id': game.team_a.season_team_cup_championship_ranking_id if game.team_a else -1,
                        'season_team_sub_cup_tournament_ranking_id': game.team_a.season_team_sub_cup_tournament_ranking_id if game.team_a else -1,
                        'season_cup_tournament_id': game.team_a.season_cup_tournament_id if game.team_a else -1,
                    },
                    'team_b': {
                        'id': game.team_b.id if game.team_b else None,
                        'name': game.team_b.name if game.team_b else 'Unknown',
                        'abbreviation': game.team_b.abbreviation if game.team_b else '',
                        'is_dummy': game.team_b.is_dummy if game.team_b else False,
                        'gbo_team': game.team_b.gbo_team if game.team_b else 0,
                        'season_team_id': game.team_b.season_team_id if game.team_b else -1,
                        'season_team_cup_tournament_ranking_id': game.team_b.season_team_cup_tournament_ranking_id if game.team_b else -1,
                        'season_team_cup_championship_ranking_id': game.team_b.season_team_cup_championship_ranking_id if game.team_b else -1,
                        'season_team_sub_cup_tournament_ranking_id': game.team_b.season_team_sub_cup_tournament_ranking_id if game.team_b else -1,
                        'season_cup_tournament_id': game.team_b.season_cup_tournament_id if game.team_b else -1,
                    },
                    'team_st_a': {
                        'id': game.team_st_a.id if game.team_st_a else -1,
                        'rank': game.team_st_a.rank if game.team_st_a else 0,
                        'team': {
                            'id': game.team_st_a.team.id if game.team_st_a and game.team_st_a.team else -1,
                            'name': game.team_st_a.team.name if game.team_st_a and game.team_st_a.team else 'Unknown',
                            'abbreviation': game.team_st_a.team.abbreviation if game.team_st_a and game.team_st_a.team else '',
                            'is_dummy': game.team_st_a.team.is_dummy if game.team_st_a and game.team_st_a.team else False,
                            'gbo_team': game.team_a.gbo_team if game.team_a else 0,
                            'season_team_id': game.team_a.season_team_id if game.team_a else -1,
                            'season_team_cup_tournament_ranking_id': game.team_a.season_team_cup_tournament_ranking_id if game.team_a else -1,
                            'season_team_cup_championship_ranking_id': game.team_a.season_team_cup_championship_ranking_id if game.team_a else -1,
                            'season_team_sub_cup_tournament_ranking_id': game.team_a.season_team_sub_cup_tournament_ranking_id if game.team_a else -1,
                            'season_cup_tournament_id': game.team_a.season_cup_tournament_id if game.team_a else -1,
                        },
                        'number_of_played_games': game.team_st_a.number_of_played_games if game.team_st_a else 0,
                        'game_points': game.team_st_a.game_points if game.team_st_a else 0,
                        'game_points_bonus': game.team_st_a.game_points_bonus if game.team_st_a else 0,
                        'ranking_points': game.team_st_a.ranking_points if game.team_st_a else 0,
                        'sets_win': game.team_st_a.sets_win if game.team_st_a else 0,
                        'sets_loose': game.team_st_a.sets_loose if game.team_st_a else 0,
                        'points_made': game.team_st_a.points_made if game.team_st_a else 0,
                        'points_received': game.team_st_a.points_received if game.team_st_a else 0,
                        'rank_initial': game.team_st_a.rank_initial if game.team_st_a else 0,
                    },
                    'team_st_b': {
                        'id': game.team_st_b.id if game.team_st_b else -1,
                        'rank': game.team_st_b.rank if game.team_st_b else 0,
                        'team': {
                            'id': game.team_st_b.team.id if game.team_st_b and game.team_st_b.team else -1,
                            'name': game.team_st_b.team.name if game.team_st_b and game.team_st_b.team else 'Unknown',
                            'abbreviation': game.team_st_b.team.abbreviation if game.team_st_b and game.team_st_b.team else '',
                            'is_dummy': game.team_st_b.team.is_dummy if game.team_st_b and game.team_st_b.team else False,
                            'gbo_team': game.team_b.gbo_team if game.team_b else 0,
                            'season_team_id': game.team_b.season_team_id if game.team_b else -1,
                            'season_team_cup_tournament_ranking_id': game.team_b.season_team_cup_tournament_ranking_id if game.team_b else -1,
                            'season_team_cup_championship_ranking_id': game.team_b.season_team_cup_championship_ranking_id if game.team_b else -1,
                            'season_team_sub_cup_tournament_ranking_id': game.team_b.season_team_sub_cup_tournament_ranking_id if game.team_b else -1,
                            'season_cup_tournament_id': game.team_b.season_cup_tournament_id if game.team_b else -1,
                        },
                        'number_of_played_games': game.team_st_b.number_of_played_games if game.team_st_b else 0,
                        'game_points': game.team_st_b.game_points if game.team_st_b else 0,
                        'game_points_bonus': game.team_st_b.game_points_bonus if game.team_st_b else 0,
                        'ranking_points': game.team_st_b.ranking_points if game.team_st_b else 0,
                        'sets_win': game.team_st_b.sets_win if game.team_st_b else 0,
                        'sets_loose': game.team_st_b.sets_loose if game.team_st_b else 0,
                        'points_made': game.team_st_b.points_made if game.team_st_b else 0,
                        'points_received': game.team_st_b.points_received if game.team_st_b else 0,
                        'rank_initial': game.team_st_b.rank_initial if game.team_st_b else 0,
                    },
                    'score_team_a_halftime_1': game.score_team_a_halftime_1,
                    'score_team_a_halftime_2': game.score_team_a_halftime_2,
                    'score_team_a_penalty': game.score_team_a_penalty,
                    'score_team_b_halftime_1': game.score_team_b_halftime_1,
                    'score_team_b_halftime_2': game.score_team_b_halftime_2,
                    'score_team_b_penalty': game.score_team_b_penalty,
                    'court': {
                        'id': game.court.id if game.court else 0,
                        'name': game.court.name if game.court else 'No Court',
                        'number': game.court.number if game.court else 0,
                    },
                    'tournament': {
                        'id': game.tournament.id if game.tournament else -1,
                        'name': game.tournament.name if game.tournament else 'No Tournament',
                        'season_cup_tournament_id': game.tournament.season_cup_tournament_id if game.tournament else -1,
                        'season_cup_german_championship_id': game.tournament.season_cup_german_championship_id if game.tournament else -1,
                    },
                    'tournament_event': serialize_tournament_event(game.tournament_event),
                    'tournament_state': serialize_tournament_state(game.tournament_state),
                } 
                for game in games
            ]
        }
    elif depth == 'medium':
        return {
            'games': [
                {
                    'id': game.id,
                    'starttime': time.mktime(game.starttime.timetuple()) if game.starttime else None,
                    'gamestate': game.gamestate,
                    'gamingstate': game.gamingstate,
                    'team_a': {
                        'id': game.team_a.id if game.team_a else None,
                        'name': game.team_a.name if game.team_a else 'Unknown',
                        'abbreviation': game.team_a.abbreviation if game.team_a else '',
                        'is_dummy': game.team_a.is_dummy if game.team_a else True,
                    },
                    'team_b': {
                        'id': game.team_b.id if game.team_b else None,
                        'name': game.team_b.name if game.team_b else 'Unknown',
                        'abbreviation': game.team_b.abbreviation if game.team_b else '',
                        'is_dummy': game.team_b.is_dummy if game.team_b else True,
                    },
                    'team_st_a': {
                        'id': game.team_st_a.id if game.team_st_a else None,
                        'rank': game.team_st_a.rank if game.team_st_a else 0,
                    },
                    'team_st_b': {
                        'id': game.team_st_b.id if game.team_st_b else None,
                        'rank': game.team_st_b.rank if game.team_st_b else 0,
                    },
                    'score_team_a_halftime_1': game.score_team_a_halftime_1,
                    'score_team_a_halftime_2': game.score_team_a_halftime_2,
                    'score_team_a_penalty': game.score_team_a_penalty,
                    'score_team_b_halftime_1': game.score_team_b_halftime_1,
                    'score_team_b_halftime_2': game.score_team_b_halftime_2,
                    'score_team_b_penalty': game.score_team_b_penalty,
                    'court': {
                        'id': game.court.id if game.court else None,
                        'name': game.court.name if game.court else 'No Court',
                        'number': game.court.number if game.court else 0,
                    },
                    'duration_of_halftime': game.duration_of_halftime,
                    'tournament_event': {
                        'id': game.tournament_event.id,
                        'name': game.tournament_event.name,
                    } if game.tournament_event else None,
                    'tournament_state': {
                        'id': game.tournament_state.id,
                        'name': game.tournament_state.name,
                        'abbreviation': game.tournament_state.abbreviation,
                    } if game.tournament_state else None,
                } 
                for game in games
            ]
        }
    
    else:  # full depth
        # For full depth, we'll still optimize compared to the original by 
        # manually constructing the dictionary with only needed fields
        return {
            'games': [
                {
                    'id': game.id,
                    'starttime': time.mktime(game.starttime.timetuple()) if game.starttime else None,
                    'gamestate': game.gamestate,
                    'gamingstate': game.gamingstate,
                    'duration_of_halftime': game.duration_of_halftime,
                    'team_a': {
                        'id': game.team_a.id if game.team_a else None,
                        'name': game.team_a.name if game.team_a else 'Unknown',
                        'abbreviation': game.team_a.abbreviation if game.team_a else '',
                        'is_dummy': game.team_a.is_dummy if game.team_a else False,
                        'gbo_team': game.team_a.gbo_team if game.team_a else 0,
                        'season_team_id': game.team_a.season_team_id if game.team_a else -1,
                        'season_team_cup_tournament_ranking_id': game.team_a.season_team_cup_tournament_ranking_id if game.team_a else -1,
                        'season_team_cup_championship_ranking_id': game.team_a.season_team_cup_championship_ranking_id if game.team_a else -1,
                        'season_team_sub_cup_tournament_ranking_id': game.team_a.season_team_sub_cup_tournament_ranking_id if game.team_a else -1,
                        'season_cup_tournament_id': game.team_a.season_cup_tournament_id if game.team_a else -1,
                    },
                    'team_b': {
                        'id': game.team_b.id if game.team_b else None,
                        'name': game.team_b.name if game.team_b else 'Unknown',
                        'abbreviation': game.team_b.abbreviation if game.team_b else '',
                        'is_dummy': game.team_b.is_dummy if game.team_b else False,
                        'gbo_team': game.team_b.gbo_team if game.team_b else 0,
                        'season_team_id': game.team_b.season_team_id if game.team_b else -1,
                        'season_team_cup_tournament_ranking_id': game.team_b.season_team_cup_tournament_ranking_id if game.team_b else -1,
                        'season_team_cup_championship_ranking_id': game.team_b.season_team_cup_championship_ranking_id if game.team_b else -1,
                        'season_team_sub_cup_tournament_ranking_id': game.team_b.season_team_sub_cup_tournament_ranking_id if game.team_b else -1,
                        'season_cup_tournament_id': game.team_b.season_cup_tournament_id if game.team_b else -1,
                    },
                    'team_st_a': {
                        'id': game.team_st_a.id if game.team_st_a else -1,
                        'rank': game.team_st_a.rank if game.team_st_a else 0,
                        'team': {
                            'id': game.team_st_a.team.id if game.team_st_a and game.team_st_a.team else -1,
                            'name': game.team_st_a.team.name if game.team_st_a and game.team_st_a.team else 'Unknown',
                            'abbreviation': game.team_st_a.team.abbreviation if game.team_st_a and game.team_st_a.team else '',
                            'is_dummy': game.team_st_a.team.is_dummy if game.team_st_a and game.team_st_a.team else False,
                            'gbo_team': game.team_a.gbo_team if game.team_a else 0,
                            'season_team_id': game.team_a.season_team_id if game.team_a else -1,
                            'season_team_cup_tournament_ranking_id': game.team_a.season_team_cup_tournament_ranking_id if game.team_a else -1,
                            'season_team_cup_championship_ranking_id': game.team_a.season_team_cup_championship_ranking_id if game.team_a else -1,
                            'season_team_sub_cup_tournament_ranking_id': game.team_a.season_team_sub_cup_tournament_ranking_id if game.team_a else -1,
                            'season_cup_tournament_id': game.team_a.season_cup_tournament_id if game.team_a else -1,
                        },
                        'number_of_played_games': game.team_st_a.number_of_played_games if game.team_st_a else 0,
                        'game_points': game.team_st_a.game_points if game.team_st_a else 0,
                        'game_points_bonus': game.team_st_a.game_points_bonus if game.team_st_a else 0,
                        'ranking_points': game.team_st_a.ranking_points if game.team_st_a else 0,
                        'sets_win': game.team_st_a.sets_win if game.team_st_a else 0,
                        'sets_loose': game.team_st_a.sets_loose if game.team_st_a else 0,
                        'points_made': game.team_st_a.points_made if game.team_st_a else 0,
                        'points_received': game.team_st_a.points_received if game.team_st_a else 0,
                        'rank_initial': game.team_st_a.rank_initial if game.team_st_a else 0,
                    },
                    'team_st_b': {
                        'id': game.team_st_b.id if game.team_st_b else -1,
                        'rank': game.team_st_b.rank if game.team_st_b else 0,
                        'team': {
                            'id': game.team_st_b.team.id if game.team_st_b and game.team_st_b.team else -1,
                            'name': game.team_st_b.team.name if game.team_st_b and game.team_st_b.team else 'Unknown',
                            'abbreviation': game.team_st_b.team.abbreviation if game.team_st_b and game.team_st_b.team else '',
                            'is_dummy': game.team_st_b.team.is_dummy if game.team_st_b and game.team_st_b.team else False,
                            'gbo_team': game.team_b.gbo_team if game.team_b else 0,
                            'season_team_id': game.team_b.season_team_id if game.team_b else -1,
                            'season_team_cup_tournament_ranking_id': game.team_b.season_team_cup_tournament_ranking_id if game.team_b else -1,
                            'season_team_cup_championship_ranking_id': game.team_b.season_team_cup_championship_ranking_id if game.team_b else -1,
                            'season_team_sub_cup_tournament_ranking_id': game.team_b.season_team_sub_cup_tournament_ranking_id if game.team_b else -1,
                            'season_cup_tournament_id': game.team_b.season_cup_tournament_id if game.team_b else -1,
                        },
                        'number_of_played_games': game.team_st_b.number_of_played_games if game.team_st_b else 0,
                        'game_points': game.team_st_b.game_points if game.team_st_b else 0,
                        'game_points_bonus': game.team_st_b.game_points_bonus if game.team_st_b else 0,
                        'ranking_points': game.team_st_b.ranking_points if game.team_st_b else 0,
                        'sets_win': game.team_st_b.sets_win if game.team_st_b else 0,
                        'sets_loose': game.team_st_b.sets_loose if game.team_st_b else 0,
                        'points_made': game.team_st_b.points_made if game.team_st_b else 0,
                        'points_received': game.team_st_b.points_received if game.team_st_b else 0,
                        'rank_initial': game.team_st_b.rank_initial if game.team_st_b else 0,
                    },
                    'score_team_a_halftime_1': game.score_team_a_halftime_1,
                    'score_team_a_halftime_2': game.score_team_a_halftime_2,
                    'score_team_a_penalty': game.score_team_a_penalty,
                    'score_team_b_halftime_1': game.score_team_b_halftime_1,
                    'score_team_b_halftime_2': game.score_team_b_halftime_2,
                    'score_team_b_penalty': game.score_team_b_penalty,
                    'court': {
                        'id': game.court.id if game.court else 0,
                        'name': game.court.name if game.court else 'No Court',
                        'number': game.court.number if game.court else 0,
                    },
                    'tournament': {
                        'id': game.tournament.id if game.tournament else -1,
                        'name': game.tournament.name if game.tournament else 'No Tournament',
                        'season_cup_tournament_id': game.tournament.season_cup_tournament_id if game.tournament else -1,
                        'season_cup_german_championship_id': game.tournament.season_cup_german_championship_id if game.tournament else -1,
                    },
                    'tournament_event': serialize_tournament_event(game.tournament_event),
                    'tournament_state': serialize_tournament_state(game.tournament_state),
                    'player_stats_team_a': [
                        serialize_playerstat(ps) 
                        for ps in getattr(game, 'player_stats', []) 
                        if game.team_a and ps.player.team_id == game.team_a.id
                    ],
                    'player_stats_team_b': [
                        serialize_playerstat(ps) 
                        for ps in getattr(game, 'player_stats', []) 
                        if game.team_b and ps.player.team_id == game.team_b.id
                    ],
                } 
                for game in games
            ]
        }


def serialize_games(games) -> Dict[str, Any]:
    return {
        'games': [serialize_game(g) for g in games]
    }

def serialize_games_list(games) -> Dict[str, Any]:
    return {
        'games': [serialize_game(g) for g in games]
    }

def serialize_tournament(t: Tournament) -> Dict[str, Any]:
    return {
        'id': t.id,
        'created_at': t.created_at,
        'name': t.name,
        'organizer': t.organizer,
        'season_tournament_id': t.season_tournament_id,
        'season_cup_tournament_id': t.season_cup_tournament_id,
        'gbo_tournament_id': t.gbo_tournament_id,
        'season_cup_german_championship_id': t.season_cup_german_championship_id,
        'season_german_championship_id': t.season_german_championship_id,
        'sub_season_cup_tournament_id': t.sub_season_cup_tournament_id,
        'tournament_event': [serialize_tournament_event(te) for te in t.tournamentevent_set.all()],
        'courts': [serialize_court_wo_tourns(c) for c in t.court_set.all()]
    }

def serialize_tournament_event(t: TournamentEvent) -> Dict[str, Any]:
    return {
        'id': t.id,
        'created_at': t.created_at,
        'name': t.name,
        'category': serialize_category(t.category),
        'season_cup_tournament_id': t.season_cup_tournament_id,
        'season_cup_german_championship_id': t.season_cup_german_championship_id,
    }

def serialize_category(t: TournamentCategory) -> Dict[str, Any]:
    return {
        'id': t.id,
        'created_at': t.created_at,
        'name': t.name,
        'category': t.category,
        'gbo_category_id': t.gbo_category_id,
        'season_tournament_category_id': t.season_tournament_category_id,
    }

def serialize_tournament_state(t: TournamentState) -> Dict[str, Any]:
    return {
        'id': t.id,
        'created_at': t.created_at,
        'name': t.name,
        'abbreviation': t.abbreviation,
    }

def serialize_court(c: Court) -> Dict[str, Any]:
    return {
        'id': c.id,
        'created_at': c.created_at,
        'name': c.name,
        'number': c.number,
        'tournament': serialize_tournament(c.tournament),
    }

def serialize_court_wo_tourns(c: Court) -> Dict[str, Any]:
    if c is None:
        return {'id': 0,
        'created_at': 0,
        'name': 'No Court',
        'number': 0,}
    return {
        'id': c.id,
        'created_at': c.created_at,
        'name': c.name,
        'number': c.number,
    }

def serialize_teamstat(stat: TeamStats) -> Dict[str, Any]:
    return {
        'id': stat.id,
        'rank': stat.rank,
        'team': serialize_team(stat.team, False),
        'number_of_played_games': stat.number_of_played_games,
        'game_points': stat.game_points,
        'game_points_bonus': stat.game_points_bonus,
        'ranking_points': stat.ranking_points,
        'sets_win': stat.sets_win,
        'sets_loose': stat.sets_loose,
        'points_made': stat.points_made,
        'points_received': stat.points_received,
        'rank_initial': stat.rank_initial,
        
    }

def serialize_team(team: Team, doWithPlayers = False) -> Dict[str, Any]:
    if team is not None:
        data = {
            'id': team.id,
            'name': team.name,
            'abbreviation': team.abbreviation,
            'gbo_team': team.gbo_team,
            'season_team_id': team.season_team_id,
            'season_team_cup_tournament_ranking_id': team.season_team_cup_tournament_ranking_id,
            'season_team_cup_championship_ranking_id': team.season_team_cup_championship_ranking_id,
            'season_team_sub_cup_tournament_ranking_id': team.season_team_sub_cup_tournament_ranking_id,
            'season_cup_tournament_id': team.season_cup_tournament_id,
            'is_dummy': team.is_dummy,
        }
        if doWithPlayers:
            data['players'] = [serialize_player(p) for p in team.player_set.all()]
        return data
    else:
        return { 'id': -1 }

def serialize_playerstat(stat: PlayerStats) -> Dict[str, Any]:
    return {
        'id': stat.id,
        'score': stat.score,
        'block_success': stat.block_success,
        'goal_keeper_success': stat.goal_keeper_success,
        'suspension': stat.suspension,
        'redcard': stat.redcard,
        'games_played': stat.games_played,
        'player': serialize_player(stat.player), 
    }

def serialize_player(player: Player) -> Dict[str, Any]:
    return {
        'id': player.id,
        'name': player.name,
        'first_name': player.first_name,
        'number': player.number,
        'team': str(player.team),
        'season_team_id': player.season_team_id,
        'season_player_id': player.season_player_id,
        'gbo_position': player.gbo_position,
        'is_active': player.is_active
    }



class TournamentTeamTransitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TournamentTeamTransition
        fields = ['id', 'tournament_event', 'origin_rank', 'target_ts_id', 'target_rank', 'comment']