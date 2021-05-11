from django.db.models.query_utils import Q
from beachhandball_app.models.choices import GAMESTATE_CHOICES
from beachhandball_app.models.Tournament import TournamentEvent, TournamentTeamTransition
from beachhandball_app.models.Game import Game
from beachhandball_app.models.Team import TeamStats, Team
from beachhandball_app.models.General import TournamentCategory
from django.utils.http import urlencode
from django.urls import reverse

def reverse_querystring(view, urlconf=None, args=None, kwargs=None, current_app=None, query_kwargs=None):
    '''Custom reverse to handle query strings.
    Usage:
        reverse('app.views.my_view', kwargs={'pk': 123}, query_kwargs={'search': 'Bob'})
    '''
    base_url = reverse(view, urlconf=urlconf, args=args, kwargs=kwargs, current_app=current_app)
    if query_kwargs:
        return '{}?{}'.format(base_url, urlencode(query_kwargs))
    return base_url


def calculate_tstate(ts):
    try:
        #ts = TournamentState.objects.get(id=tstate)

        tstats = TeamStats.objects.filter(tournamentstate=ts).all()

        for tst in tstats:
            tst.number_of_played_games = 0
            tst.game_points = 0
            tst.game_points_bonus = 0
            tst.ranking_points = 0
            tst.sets_win = 0
            tst.sets_loose = 0
            tst.points_made = 0
            tst.points_received = 0
            tst.save()

        games = Game.objects.all().filter(tournament=ts.tournament_event,
                                          tournament_state=ts,
                                          gamestate='FINISHED')

        for g in games:
            #teama_stats = TeamStats.objects.filter(tournament_event=g.tournament,
            #                                       tournamentstate=g.tournament_state,
            #                                       team=g.team_a)[:1].get()
            #teamb_stats = TeamStats.objects.filter(tournament_event=g.tournament,
            #                                       tournamentstate=g.tournament_state,
            #                                       team=g.team_b)[:1].get()
            teama_stats = g.team_st_a
            teamb_stats = g.team_st_b
            iSetH = 0
            iSetA = 0
            if getIntVal(g.score_team_a_halftime_1) > getIntVal(
                   g.score_team_b_halftime_1):
                iSetH += 1
            elif getIntVal(g.score_team_a_halftime_1) < getIntVal(
                    g.score_team_b_halftime_1):
                iSetA += 1

            if getIntVal(g.score_team_a_halftime_2) > getIntVal(
                    g.score_team_b_halftime_2):
                iSetH += 1
            elif getIntVal(g.score_team_a_halftime_2) < getIntVal(
                    g.score_team_b_halftime_2):
                iSetA += 1

            if getIntVal(g.score_team_a_penalty) > getIntVal(
                    g.score_team_b_penalty):
                iSetH += 1
            elif getIntVal(g.score_team_a_penalty) < getIntVal(
                    g.score_team_b_penalty):
                iSetA += 1

            actGamesWinA = getIntVal(teama_stats.game_points)
            nPlayedGamesA = getIntVal(teama_stats.number_of_played_games)
            actGamesWinB = getIntVal(teamb_stats.game_points)
            nPlayedGamesB = getIntVal(teamb_stats.number_of_played_games)

            teama_stats.number_of_played_games = nPlayedGamesA + 1
            teamb_stats.number_of_played_games = nPlayedGamesB + 1

            if iSetH > iSetA:
                teama_stats.game_points = actGamesWinA + 2
                teama_stats.ranking_points = actGamesWinA + 2
            else:
                teamb_stats.game_points = actGamesWinB + 2
                teamb_stats.ranking_points = actGamesWinB + 2

            actSetsWinA = getIntVal(teama_stats.sets_win)
            actSetsLooseA = getIntVal(teama_stats.sets_loose)
            actPointsMadeA = getIntVal(teama_stats.points_made)
            actPointsRecA = getIntVal(teama_stats.sets_loose)

            pointsMa = getIntVal(g.score_team_a_halftime_1) + \
                       getIntVal(g.score_team_a_halftime_2) + \
                       getIntVal(g.score_team_a_penalty)

            pointsMb = getIntVal(g.score_team_b_halftime_1) + \
                       getIntVal(g.score_team_b_halftime_2) + \
                       getIntVal(g.score_team_b_penalty)

            teama_stats.sets_win = actSetsWinA + iSetH
            teama_stats.sets_loose = actSetsLooseA + iSetA
            teama_stats.points_made = actPointsMadeA + pointsMa
            teama_stats.points_received = actPointsRecA + pointsMb

            actSetsWinB = getIntVal(teamb_stats.sets_win)
            actSetsLooseB = getIntVal(teamb_stats.sets_loose)
            actPointsMadeB = getIntVal(teamb_stats.points_made)
            actPointsRecB = getIntVal(teamb_stats.points_received)

            teamb_stats.sets_win = actSetsWinB + iSetA
            teamb_stats.sets_loose = actSetsLooseB + iSetH
            teamb_stats.points_made = actPointsMadeB + pointsMb
            teamb_stats.points_received = actPointsRecB + pointsMa

            teama_stats.save()
            teamb_stats.save()
            g.gamingstate = 'Finished'
            g.save()
        check_direct_compare(ts)
        check_tournamentstate_finished(ts.tournament_event, ts)
    except Exception as e:
        print(e)
    finally:
        print('')

def check_direct_compare(ts):

    # get
    if ts.direct_compare and Game.objects.all().filter(tournament=ts.tournament_event,
                                                       tournament_state=ts,
                                                       gamestate=GAMESTATE_CHOICES[2][1]).count() > 0:
        # detect direct compares
        g_pts = 0
        team_list = []
        # get all TeamStats in tourstate
        teamstats = TeamStats.objects.all().filter(tournament_event=ts.tournament_event, tournamentstate=ts)
        # clear all old  direct compare calcs
        teamstats.update(game_points_bonus=0)

        # loop over them and check for direct compare
        for teamstat in teamstats:
            # all teamstats with same game_points
            teamst = TeamStats.objects.all().filter(tournament_event=ts.tournament_event, tournamentstate=ts,
                                                    game_points=teamstat.game_points,
                                                    game_points_bonus=teamstat.game_points_bonus)
            if teamst.count() == 2:
                games = Game.objects.all().filter(Q(team_a=teamst[0].team) | Q(team_b=teamst[0].team),
                                                  tournament=ts.tournament, tournament_state=ts)
                games = games.filter(Q(team_a=teamst[1].team) | Q(team_b=teamst[1].team),
                                     gamestate=GAMESTATE_CHOICES[2][1])
                if games.count() > 0:
                    teamstat = TeamStats.objects.get(team=get_game_winner(games.get()))
                    teamstat.game_points_bonus = 1
                    teamstat.save()

            elif teamst.count() > 2:
                print("")

def check_tournamentstate_finished(tevent, ts):
    games_played = Game.objects.all().filter(tournament=tevent,
                                             tournament_state=ts,
                                             gamestate=GAMESTATE_CHOICES[2][1]).count()

    all_games = Game.objects.all().filter(tournament=tevent,
                                          tournament_state=ts).count()

    # check if all games are FINISHED
    if games_played == all_games:
        # get teamstats
        teamstats = TeamStats.objects.filter(tournament_event=tevent,
                                            tournament_state=ts).order_by('-ranking_points')

        iRank = 1
        for stat in teamstats:
            # get TournamentTeamTransition
            trans = TournamentTeamTransition.objects.filter(tournament_event=tevent,
                                                            origin_ts_id=ts,
                                                            origin_rank=iRank)

            if trans.count() > 0:
                trans = trans.get()
                target_stat = TeamStats.objects.all().filter(tournament_event=tevent,
                                                             tournamentstate=trans.target_ts_id,
                                                             rank_initial=trans.target_rank)
                if target_stat.count() == 1:
                    target_stat = target_stat.get()
                    target_stat.team = stat.team
                    if trans.keep_stats:
                        target_stat.number_of_played_games = 0
                        target_stat.sets_win = stat.sets_win
                        target_stat.sets_loose = stat.sets_loose
                        target_stat.points_made = stat.points_made
                        target_stat.points_received = stat.points_received
                        target_stat.game_points = stat.game_points
                    target_stat.game_points_bonus = 0
                    target_stat.save()

            iRank = iRank + 1

def create_teams_testdata(tevent):
    tevent = TournamentEvent.objects.get(id=tevent)
    tcat = TournamentCategory.objects.get(id=1)
    act_team_st, cr = Team.objects.get_or_create(tournament_event=tevent,
                                                name='DreamTeam',
                                                abbreviation='DT',
                                                gbo_team=0,
                                                category=tcat)
    act_team_st.save()
    act_team_st, cr = Team.objects.get_or_create(tournament_event=tevent,
                                                name='The Beachers',
                                                abbreviation='TBS',
                                                gbo_team=0,
                                                category=tcat)
    act_team_st.save()
    act_team_st, cr = Team.objects.get_or_create(tournament_event=tevent,
                                                name='SuperStars',
                                                abbreviation='SuS',
                                                gbo_team=0,
                                                category=tcat)
    act_team_st.save()
    act_team_st, cr = Team.objects.get_or_create(tournament_event=tevent,
                                                name='Beach Easy Team',
                                                abbreviation='BET',
                                                gbo_team=0,
                                                category=tcat)
    act_team_st.save()
    act_team_st, cr = Team.objects.get_or_create(tournament_event=tevent,
                                                name='DumpHeads',
                                                abbreviation='DH',
                                                gbo_team=0,
                                                category=tcat)
    act_team_st.save()
    act_team_st, cr = Team.objects.get_or_create(tournament_event=tevent,
                                                name='FlyingKack',
                                                abbreviation='FK',
                                                gbo_team=0,
                                                category=tcat)
    act_team_st.save()
    act_team_st, cr = Team.objects.get_or_create(tournament_event=tevent,
                                                name='The Gang',
                                                abbreviation='TGA',
                                                gbo_team=0,
                                                category=tcat)
    act_team_st.save()
    act_team_st, cr = Team.objects.get_or_create(tournament_event=tevent,
                                                name='Loosers',
                                                abbreviation='Loo',
                                                gbo_team=0,
                                                category=tcat)
    act_team_st.save()

def get_game_winner(game):
    if game.winner_halftime_1 == game.winner_halftime_2:
        return game.winner_halftime_1
    else:
        return game.winner_halftime_penalty

def getIntVal(val):
    if val is not None:
        return val
    else:
        return 0