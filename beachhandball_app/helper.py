from beachhandball_app.models.Tournament import TournamentEvent
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
            teama_stats = TeamStats.objects.filter(tournament_event=g.tournament,
                                                   tournamentstate=g.tournament_state,
                                                   team=g.team_a)[:1].get()
            teamb_stats = TeamStats.objects.filter(tournament_event=g.tournament,
                                                   tournamentstate=g.tournament_state,
                                                   team=g.team_b)[:1].get()
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
        #check_direct_compare(ts)
    except:
        print('')
    finally:
        print('')

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

def getIntVal(val):
    if val is not None:
        return val
    else:
        return 0