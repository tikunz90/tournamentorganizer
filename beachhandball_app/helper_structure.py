

from beachhandball_app.models.Team import Team, TeamStats
from beachhandball_app.models.Tournaments import TournamentState, TournamentTeamTransition


def tstate_add_team(pk_tevent, pk_tstate, num_teams):
    result = {'isError': False, 'msg': ''}
    try:
        state = TournamentState.objects.get(id=pk_tstate)
        tstats = TeamStats.objects.filter(tournamentstate=state).all()
        tstats = [t for t in tstats]
        new_rank = len(tstats) + 1
        for i in range(num_teams):
            print()
            new_dummy_team, cr = Team.objects.get_or_create(tournament_event=state.tournament_event,
                                tournamentstate=state,
                                name="{}. {}".format(new_rank, state),
                                abbreviation="{}.{}".format(new_rank, state.abbreviation),
                                category=state.tournament_event.category,
                                season_cup_tournament_id=state.tournament_event.season_cup_tournament_id,
                                is_dummy=True)
            act_team_st, cr = TeamStats.objects.get_or_create(tournament_event=state.tournament_event,
                            tournamentstate=state,
                            team=new_dummy_team,
                            rank_initial=new_rank,
                            rank=new_rank)
            ttt, cr = TournamentTeamTransition.objects.get_or_create(tournament_event=state.tournament_event,
                                                    origin_ts_id=state,
                                                    origin_rank=new_rank,
                                                    target_rank=0)
            new_rank += 1
    except Exception as ex:
        result['isError'] = True
        result['msg'] = ex.message
    return result

def tstate_delete_team(pk_tevent, pk_tstate):
    result = {'isError': False, 'msg': 'Success deleting team'}
    try:
        state = TournamentState.objects.get(id=pk_tstate)
        tstats = TeamStats.objects.filter(tournamentstate=state).all()
        tstats = [t for t in tstats]
        last_rank = len(tstats)
        last_tstat = [t for t in tstats if t.rank == last_rank][0]
        ttt = TournamentTeamTransition.objects.filter(origin_ts_id=state, origin_rank=last_rank).first()
        if not ttt is None:
            ttt.delete()

        if last_tstat.team.is_dummy is True:
            last_tstat.team.delete()
        last_tstat.delete()

        
    except Exception as ex:
        result['isError'] = True
        result['msg'] = str(ex)
    return result