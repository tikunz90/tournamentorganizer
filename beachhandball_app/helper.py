
from datetime import datetime
from beachhandball_app.models.Player import Player
from django.db.models.query_utils import Q
from beachhandball_app.models.choices import GAMESTATE_CHOICES
from beachhandball_app.models.Tournaments import Tournament, TournamentEvent, TournamentSettings, TournamentState, TournamentTeamTransition
from beachhandball_app.models.Game import Game
from beachhandball_app.models.Team import Coach, TeamStats, Team
from beachhandball_app.models.General import TournamentCategory
from django.utils.http import urlencode
from django.urls import reverse

from beachhandball_app.services.services import SWS

def update_user_tournament(gbouser):
    print("ENTER update_user_tournamet")
    gbo_data = gbouser.gbo_data
    if gbo_data['isError'] == 'true':
        return None
    gbo_data = gbo_data['message']

    for gbot in gbo_data:
        tourn_found = False
        
        season_tourn = gbot['seasonTournament']
        gbo_tourn = season_tourn['tournament']

        to_tourn = None
        tourns = Tournament.objects.filter(organizer=gbouser.subject_id)
        for t in tourns:
            if t.season_tournament_id == gbot['id']:
                print("Found season_tourn")
                to_tourn = t
                tourn_found = True
                t.organizer=gbouser.subject_id
                t.name=gbo_tourn['name']
                t.last_sync_at=datetime.now()
                t.season_tournament_id=season_tourn['id']
                t.season_cup_tournament_id=gbot['id']
                t.save()
                ts, cr = TournamentSettings.objects.get_or_create(tournament=t)
                ts.save()
        if not tourn_found:
            #create tournament
            new_t = Tournament(organizer=gbouser.subject_id,
            name=gbo_tourn['name'],
            last_sync_at=datetime.now(),
            season_tournament_id=season_tourn['id'],
            season_cup_tournament_id=gbot['id'])
            new_t.save()
            ts, cr = TournamentSettings.objects.get_or_create(tournament=new_t)
            ts.save()
            to_tourn = new_t
    

def update_user_tournament_events(gbouser, to_tourn):
    print("ENTER update_user_tournament_events")
    gbo_data = gbouser.gbo_data
    if gbo_data['isError'] == 'true':
        return None
    gbo_data = gbo_data['message']

    for gbot in gbo_data:
        season_tourn = gbot['seasonTournament']
        # read dates
        if not season_tourn['seasonTournamentWeeks']:
            print("Not weeks defined")
        start_ts = int(season_tourn['seasonTournamentWeeks'][0]['seasonWeek']['start_at_ts'])/1000
        end_ts = int(season_tourn['seasonTournamentWeeks'][0]['seasonWeek']['end_at_ts'])/1000

        # scann categories and update/create events
        for cat in season_tourn['seasonTournamentCategories']:
            tcat = None
            te = None
            abbrv = 'W'
            if cat['category']['gender']['name'] == 'man':
                abbrv = 'M'
            
            tcats = TournamentCategory.objects.filter(season_tournament_category_id=cat['id'])
            if tcats.count() == 0:
                tcat, cr = TournamentCategory.objects.get_or_create(
                    gbo_category_id=cat['category']['id'],
                    classification=cat['category']['name'],
                    name=cat['category']['gender']['name'],
                    category=cat['category']['gender']['name'],
                    abbreviation=abbrv)
     
                tcat.season_tournament_category_id=cat['id']
                tcat.save()
            else:
                tcat = tcats.first()

            tevents = TournamentEvent.objects.filter(tournament=to_tourn,season_tournament_category_id=tcat.season_tournament_category_id, season_cup_tournament_id=gbot['id'])
            if tevents.count() == 0:
                te = TournamentEvent(tournament_id=to_tourn.id,
                    season_tournament_category_id=cat['id'],
                    season_cup_tournament_id=gbot['id'],
                    season_tournament_id=season_tourn['id'],
                    name=to_tourn.name,
                    category=tcat,
                    start_ts=datetime.fromtimestamp(start_ts),
                    end_ts=datetime.fromtimestamp(end_ts),
                    max_number_teams=16,
                    last_sync_at=datetime.now())      
            else:
                te = tevents.first()
                te.tournament=to_tourn
                te.name=to_tourn.name
                te.category=tcat
                te.start_ts=datetime.fromtimestamp(start_ts)
                te.end_ts=datetime.fromtimestamp(end_ts)
                te.max_number_teams=4
                te.last_sync_at=datetime.now()
            te.save()

            # team
            team_ranked = []#SWS.getTeamsOfTournamentById(gbouser, season_tourn['id'])
            #team_requests = season_tourn['requestSeasonTeamTournaments']
            data = SWS.getSeasonTeamCupTournamentRanking(gbouser)
            if data['isError'] is True:
                print(data['message'])
                continue

            sync_teams(gbouser, te, data)

            for team_item in team_ranked:
                teams = Team.objects.filter(season_team_cup_tournament_ranking_id=team_item['id'])
                if teams.count() == 0:
                    data_tt = SWS.getTeamTournamentById(gbouser, team_item['seasonTeam'])
                    data_team = SWS.getSeasonActive(gbouser, data_tt['seasonTeam']['id'])
                    team = Team(request_season_team_tournaments_id=team_item['id'],
                    gbo_team = data_team['id'],
                    season_team_id=team_item['seasonTeam']['id'],
                    tournament_event=te,
                    name=data_team['team']['name'],
                    abbreviation=data_team['team']['name_abbreviated'])
            

    print("EXIT update_user_tournament")


def sync_teams(gbouser, tevent, data):
    response = SWS.getTeams(gbouser)
    if response['isError'] is True:
        return
    teams_data = response['message']
    team_cup_tournament_rankings = data['message']
    for ranking in team_cup_tournament_rankings:
        if tevent.season_cup_tournament_id != ranking['seasonCupTournament']['id']:
            continue
        if tevent.category.gbo_category_id != ranking['seasonTeam']['team']['category']['id']:
            continue
        act_team = None

        act_team, cr = Team.objects.get_or_create(season_team_cup_tournament_ranking_id=ranking['id'],
        tournament_event=tevent)
        act_team.gbo_team = ranking['seasonTeam']['team']['id']
        act_team.season_team_id = ranking['seasonTeam']['id']
        act_team.season_team_cup_tournament_ranking_id = ranking['id']
        act_team.name = ranking['seasonTeam']['team']['name']
        act_team.abbreviation = ranking['seasonTeam']['team']['name_abbreviated']
        act_team.category = tevent.category
        act_team.is_dummy = False
        act_team.save()

        season_team = None
        for st in teams_data:
            if st['id'] == act_team.season_team_id:
                season_team = st

        if season_team is None:
            return

        for season_player in season_team['seasonPlayers']:
            act_player, cr = Player.objects.get_or_create(season_team_id=act_team.season_team_id, season_player_id=season_player['id'], number=season_player['number'])
            act_player.tournament_event = tevent
            act_player.team = act_team
            act_player.name = season_player['seasonSubject']['subject']['user']['family_name']
            act_player.first_name = season_player['seasonSubject']['subject']['user']['name']
            act_player.gbo_position = season_player['seasonSubject']['subject']['subjectLevel']['name']
            is_active = False
            for activeplayer in ranking['seasonPlayersInTournament']:
                if activeplayer['seasonPlayer']['id'] == season_player['id']:
                    is_active = True
            act_player.is_active = is_active
            act_player.number = season_player['number']
            act_player.season_team_id = act_team.season_team_id
            act_player.season_player_id = season_player['id']
            act_player.save()
        
        # Coaches
        for season_coach in season_team['seasonCoaches']:
            act_coach, cr = Coach.objects.get_or_create(season_team_id=act_team.season_team_id, season_coach_id=season_coach['id'])
            act_coach.tournament_event = tevent
            act_coach.team = act_team
            act_coach.name = season_coach['seasonSubject']['subject']['user']['family_name']
            act_coach.first_name = season_coach['seasonSubject']['subject']['user']['name']
            act_coach.gbo_position = season_coach['seasonSubject']['subject']['subjectLevel']['name']
            act_coach.season_team_id = act_team.season_team_id
            act_coach.season_coach_id = season_coach['id']
            act_coach.save()


    return

def update_team(gbouser, team_id):
    return

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

        games = Game.objects.all().filter(tournament_event=ts.tournament_event,
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
            actPointsRecA = getIntVal(teama_stats.points_received)

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
            g.calc_winner()
            g.save()
        if not ts.direct_compare:
            teamstatsquery = _do_table_ordering(TeamStats.objects.filter(tournamentstate=ts))
            teamstats = teamstatsquery.all()
            max_val = teamstats.count()
            for tstat in teamstats:
                tstat.ranking_points = tstat.ranking_points + max_val
                max_val = max_val - 1
                tstat.save()

        else:    
            check_direct_compare(ts)
        #check_tournamentstate_finished(ts.tournament_event, ts)
    except Exception as e:
        print(e)
    finally:
        print('')

def _do_table_ordering(queryset):
    return queryset.extra(
        select={'points_difference': 'points_made - points_received'}
    ).extra(
        select={'sets_difference': 'sets_win - sets_loose'}
    ).extra(
        select={'game_points_sum': 'game_points + game_points_bonus'}
    ).order_by(
        '-game_points_sum', '-sets_difference', '-points_difference', '-points_made'
    )

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
                                                  tournament_event=ts.tournament_event, tournament_state=ts)
                games = games.filter(Q(team_a=teamst[1].team) | Q(team_b=teamst[1].team),
                                     gamestate=GAMESTATE_CHOICES[2][1])
                if games.count() > 0:
                    teamstat = TeamStats.objects.get(team=get_game_winner(games.get()))
                    teamstat.game_points_bonus = 1
                    teamstat.save()

            elif teamst.count() > 2:
                print("")

def check_all_tournamentstate_finshed(tevent):
    tstates = TournamentState.objects.filter(tournament_event=tevent)
    for ts in tstates:
        games_played = Game.objects.all().filter(tournament_event=tevent,
                                             tournament_state=ts,
                                             gamestate=GAMESTATE_CHOICES[2][1]).count()

        all_games = Game.objects.all().filter(tournament_event=tevent,
                                                tournament_state=ts).count()
        if games_played == all_games:
            ts.is_finished = True
        else:
            ts.is_finished = False
        ts.save(update_fields=['is_finished'])

def check_tournamentstate_finished(tevent, ts):
    games_played = Game.objects.all().filter(tournament_event=tevent,
                                             tournament_state=ts,
                                             gamestate=GAMESTATE_CHOICES[2][1]).count()

    all_games = Game.objects.all().filter(tournament_event=tevent,
                                          tournament_state=ts).count()

    # check if all games are FINISHED
    if games_played == all_games:
        # get teamstats
        teamstats = TeamStats.objects.filter(tournament_event=tevent,
                                            tournamentstate=ts).order_by('-ranking_points')

        iRank = 1
        for stat in teamstats:
            # get TournamentTeamTransition
            trans = TournamentTeamTransition.objects.filter(tournament_event=tevent,
                                                            origin_ts_id=ts,
                                                            is_executed=False,
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
                    target_stat.ranking_points = 0
                    target_stat.save()
                trans.is_executed = True
                trans.save(update_fields=['is_executed'])

            iRank = iRank + 1

        # check if all trans of tstate are done
        num_trans = TournamentTeamTransition.objects.filter(tournament_event=tevent,
                                                            origin_ts_id=ts,
                                                            is_executed=False).count()
        if num_trans > 0:
            ts.transitions_done = False
        else:
            ts.transitions_done = True
        ts.save(update_fields=['transitions_done'])



def create_teams_testdata(tevent):
    tevent = TournamentEvent.objects.get(id=tevent)
    tcat = TournamentCategory.objects.get(id=1)
    max_teams = tevent.max_number_teams
    names = ('DreamTeam', 'The Beachers','SuperStars','Beach Easy Team','DumpHeads','FlyingKack','The Gang','Loosers',)
    abb = ('DT', 'TBS','SuS','BET','DH','FK','TGA','Loo',)
    for iTeam in range(0, max_teams):
        act_team_st, cr = Team.objects.get_or_create(tournament_event=tevent,
                                                    name=names[iTeam],
                                                    abbreviation=abb[iTeam],
                                                    gbo_team=0,
                                                    category=tcat)
        act_team_st.save()
        for i in range(1, 11):
            act_player, cr = Player.objects.get_or_create(tournament_event=tevent,
                                                            first_name=f'FName{i}',
                                                            name=f'Name{i}',
                                                            team=act_team_st,
                                                            number=i)
            act_player.save()


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