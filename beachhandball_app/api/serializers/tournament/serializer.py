from typing import Dict, Any

from rest_framework import routers, serializers, viewsets

from beachhandball_app.models.Tournaments import Tournament, TournamentEvent, TournamentStage, TournamentState
from beachhandball_app.models.General import TournamentCategory
from beachhandball_app.models.Team import Team, TeamStats
from beachhandball_app.models.Player import Player, PlayerStats

class TournamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournament
        fields = ('id', 'name', 'created_at', 'is_active', 'last_sync_at', 'season_tournament_id', 'season_cup_tournament_id')
        depth = 0

def serialize_tournament(tournament: Tournament) -> Dict[str, Any]:
    return {
        'id': tournament.id,
        'created_at': tournament.created_at,#tournament.starttime.strftime('%H:%M (%d.%m.%Y)'),
        'is_active': tournament.is_active,
        'last_sync_at': tournament.last_sync_at,
        'season_tournament_id': tournament.season_tournament_id,
        'season_cup_tournament_id': tournament.season_cup_tournament_id,
        'events': [serialize_tournament_event(event) for event in tournament.all_tevents]
    }

def serialize_tournament_event(tournamentEvent: TournamentEvent) -> Dict[str, Any]:
    return {
        'id': tournamentEvent.id,
        'name': tournamentEvent.name,
        'category': serialize_tournament_category(tournamentEvent.category),
        'stages': [serialize_tournament_stage(stage) for stage in tournamentEvent.all_tstages],
        'top10_player_stats_offense': [serialize_playerstat(stat) for stat in tournamentEvent.top10_player_stats_offense[:10]],
        'top10_player_stats_defense': [serialize_playerstat(stat) for stat in tournamentEvent.top10_player_stats_defense[:10]],
        'top10_player_stats_gk': [serialize_playerstat(stat) for stat in tournamentEvent.top10_player_stats_gk[:10]]
    }

def serialize_tournament_category(category: TournamentCategory) -> Dict[str, Any]:
    return {
        'id': category.id,
        'name': category.name,
        'category': category.category,
        'gbo_category_id': category.gbo_category_id,
        'season_tournament_category_id': category.season_tournament_category_id,
    }

def serialize_tournament_stage(stage: TournamentStage) -> Dict[str, Any]:
    return {
        'id': stage.id,
        'name': stage.name,
        'tournament_stage': stage.tournament_stage,
        'order': stage.order,
        'states': [serialize_tournament_state(state) for state in stage.all_tstates]
    }

def serialize_tournament_state(state: TournamentState) -> Dict[str, Any]:
    return {
        'id': state.id,
        'abbreviation': state.abbreviation,
        'hierarchy': state.hierarchy,
        'max_number_teams': state.max_number_teams,
        'min_number_teams': state.min_number_teams,
        'is_final': state.is_final,
        'is_finished': state.is_finished,
        'ranking': [serialize_teamstat(stat) for stat in state.all_team_stats]
    }

def serialize_teamstat(stat: TeamStats) -> Dict[str, Any]:
    return {
        'id': stat.id,
        'rank': stat.rank,
        'team': serialize_team(stat.team),
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

def serialize_team(team: Team) -> Dict[str, Any]:
    return {
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
    }