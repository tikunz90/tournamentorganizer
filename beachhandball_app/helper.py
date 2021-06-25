import unicodedata
from datetime import datetime

from django.db.models.query import Prefetch
from beachhandball_app.models.Player import Player
from django.db.models.query_utils import Q, check_rel_lookup_compatibility
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

    print("season_cup_tournament...")
    gbo_data = gbouser.gbo_data
    if not gbo_data['isError']:
        gbo_data = gbo_data['message']

        for gbot in gbo_data:
            tourn_found = False
            
            season_tourn = gbot['seasonTournament']
            gbo_tourn = season_tourn['tournament']

            to_tourn = None
            tourns = Tournament.objects.filter(organizer=gbouser.subject_id, season_cup_tournament_id=gbot['id'])
            tourns_by_season_cup_id = Tournament.objects.filter(season_cup_tournament_id=gbot['id'])
            for t in tourns:
                if t.season_tournament_id == season_tourn['id']:
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
            if not tourn_found and tourns_by_season_cup_id.count() == 0:
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
            else:
                print("Tournament exists but is assigned to other user")

    print("season_cup_german_championship")
    gbo_data = gbouser.gbo_gc_data
    if not gbo_data['isError']:
        gbo_data = gbo_data['message']

        for gbot in gbo_data:
            tourn_found = False
            
            season_tourn = gbot['seasonTournament']
            gbo_tourn = season_tourn['tournament']

            to_tourn = None
            tourns = Tournament.objects.filter(organizer=gbouser.subject_id, season_cup_german_championship_id=gbot['id'])
            tourns_by_season_cup_id = Tournament.objects.filter(season_cup_german_championship_id=gbot['id'])
            for t in tourns:
                if t.season_german_championship_id == season_tourn['id']:
                    print("Found season_tourn")
                    to_tourn = t
                    tourn_found = True
                    t.organizer=gbouser.subject_id
                    t.name=gbo_tourn['name']
                    t.last_sync_at=datetime.now()
                    t.season_german_championship_id=season_tourn['id']
                    t.season_cup_german_championship_id=gbot['id']
                    t.save()
                    ts, cr = TournamentSettings.objects.get_or_create(tournament=t)
                    ts.save()
            if not tourn_found and tourns_by_season_cup_id.count() == 0:
                #create tournament
                new_t = Tournament(organizer=gbouser.subject_id,
                name=gbo_tourn['name'],
                last_sync_at=datetime.now(),
                season_german_championship_id=season_tourn['id'],
                season_cup_german_championship_id=gbot['id'])
                new_t.save()
                ts, cr = TournamentSettings.objects.get_or_create(tournament=new_t)
                ts.save()
                to_tourn = new_t
            else:
                print("Tournament exists but is assigned to other user")
    print("sub-season")
    return
    gbo_data = gbouser.gbo_sub_data
    if not gbo_data['isError']:
        gbo_data = gbo_data['message']

        for gbot in gbo_data:
            tourn_found = False
            
            season_tourn = gbot['seasonTournament']
            gbo_tourn = season_tourn['tournament']

            to_tourn = None
            tourns = Tournament.objects.filter(organizer=gbouser.subject_id)
            tourns_by_season_cup_id = Tournament.objects.filter(sub_season_cup_tournament_id=gbot['id'])
            for t in tourns:
                if t.season_tournament_id == gbot['id']:
                    print("Found season_tourn")
                    to_tourn = t
                    tourn_found = True
                    t.organizer=gbouser.subject_id
                    t.name=gbo_tourn['name']
                    t.last_sync_at=datetime.now()
                    t.season_tournament_id=season_tourn['id']
                    t.sub_season_cup_tournament_id=gbot['id']
                    t.save()
                    ts, cr = TournamentSettings.objects.get_or_create(tournament=t)
                    ts.save()
            if not tourn_found and tourns_by_season_cup_id.count() == 0:
                #create tournament
                new_t = Tournament(organizer=gbouser.subject_id,
                name=gbo_tourn['name'],
                last_sync_at=datetime.now(),
                season_tournament_id=season_tourn['id'],
                sub_season_cup_tournament_id=gbot['id'])
                new_t.save()
                ts, cr = TournamentSettings.objects.get_or_create(tournament=new_t)
                ts.save()
                to_tourn = new_t
            else:
                print("Tournament exists but is assigned to other user")

def update_user_tournament_events(gbouser, to_tourn):
    print("ENTER update_user_tournament_events")
    cup_type = 'is_cup'
    if to_tourn.season_cup_tournament_id != 0:
        gbo_data = gbouser.gbo_data
        cup_type = 'is_cup'
    elif to_tourn.season_cup_german_championship_id != 0:
        gbo_data = gbouser.gbo_gc_data
        cup_type = 'is_gc'
    elif to_tourn.sub_season_cup_tournament_id != 0:
        gbo_data = gbouser.gbo_sub_data
        cup_type = 'is_sub'
    else:
        print("No ID to any gbo tournament")
        return
    if not gbo_data['isError']:
        gbo_data = gbo_data['message']

        for gbot in gbo_data:
            season_tourn = gbot['seasonTournament']
            if cup_type == 'is_cup' and season_tourn['tournament']['id'] != to_tourn.season_tournament_id:
                continue
            elif cup_type == 'is_gc' and season_tourn['tournament']['id'] != to_tourn.season_german_championship_id:
                continue
            elif cup_type == 'is_sub':
                continue
                
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
                if cup_type == 'is_cup':
                    tevents = TournamentEvent.objects.filter(tournament=to_tourn,season_tournament_category_id=tcat.season_tournament_category_id, season_cup_tournament_id=gbot['id'])
                elif cup_type == 'is_gc':
                    tevents = TournamentEvent.objects.filter(tournament=to_tourn,season_tournament_category_id=tcat.season_tournament_category_id, season_cup_german_championship_id=gbot['id'])
                elif cup_type == 'is_sub':
                    tevents = TournamentEvent.objects.filter(tournament=to_tourn,season_tournament_category_id=tcat.season_tournament_category_id, sub_season_cup_tournament_id=gbot['id'])
                
                if tevents.count() == 0:  
                    if cup_type == 'is_cup':
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
                    elif cup_type == 'is_gc':
                        te = TournamentEvent(tournament_id=to_tourn.id,
                            season_tournament_category_id=cat['id'],
                            season_cup_german_championship_id=gbot['id'],
                            season_tournament_id=season_tourn['id'],
                            name=to_tourn.name,
                            category=tcat,
                            start_ts=datetime.fromtimestamp(start_ts),
                            end_ts=datetime.fromtimestamp(end_ts),
                            max_number_teams=16,
                            last_sync_at=datetime.now())
                    elif cup_type == 'is_sub':
                        te = TournamentEvent(tournament_id=to_tourn.id,
                            season_tournament_category_id=cat['id'],
                            sub_season_cup_tournament_id=gbot['id'],
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
                    te.max_number_teams=16
                    te.last_sync_at=datetime.now()
                te.save()

                # team
                if cup_type == 'is_cup':
                    data = SWS.getSeasonTeamCupTournamentRanking(gbouser)
                elif cup_type == 'is_gc':
                    data = SWS.getSeasonTeamCupChampionshipRanking(gbouser)
                elif cup_type == 'is_sub':
                    data = SWS.getSeasonTeamSubCupTournamentRanking(gbouser)
                
                if data['isError'] is True:
                    print(data['message'])
                    continue
                
                sync_teams(gbouser, te, data, cup_type)              
                
    print("EXIT update_user_tournament_events")


def sync_teams(gbouser, tevent, data, cup_type):
    response = SWS.getTeams(gbouser)
    if response['isError'] is True:
        return
    
    team_data_q = Team.objects.select_related("tournament_event").prefetch_related(
        Prefetch("player_set", queryset=Player.objects.select_related("tournament_event").all(), to_attr="players"),
        Prefetch("coach_set", queryset=Coach.objects.select_related("tournament_event").all(), to_attr="coaches")
    ).all()
    my_team_data = [team for team in team_data_q if not team.is_dummy and team.tournament_event.id == tevent.id]
    my_dummy_team_data = [team for team in team_data_q if team.is_dummy and team.tournament_event.id == tevent.id]    
    
    teams_data = response['message']
    team_cup_tournament_rankings = data['message']
    team_bulk_list = []
    season_cup_tourn_id_for_dummy = 0;
    for ranking in team_cup_tournament_rankings:
        if cup_type == 'is_cup' and tevent.season_cup_tournament_id != ranking['seasonCupTournament']['id']:
            continue
        if cup_type == 'is_gc' and tevent.season_cup_german_championship_id != ranking['seasonCupTournament']['id']:
            continue
        if cup_type == 'is_sub' and tevent.sub_season_cup_tournament_id != ranking['seasonCupTournament']['id']:
            continue
        if tevent.category.gbo_category_id != ranking['seasonTeam']['team']['category']['id']:
            continue
        season_cup_tourn_id_for_dummy = ranking['seasonCupTournament']['id']
        player_bulk_update_list = []
        player_bulk_create_list = []
        coach_bulk_update_list = []
        coach_bulk_create_list = []
        players_list = []
        coaches_list = []
        act_team = next((x for x in my_team_data if x.season_team_cup_tournament_ranking_id==ranking['id']), None)
        if not act_team is None:
            players_list = act_team.players
            coaches_list = act_team.coaches
        if act_team is None and cup_type == 'is_cup':
            act_team, cr = Team.objects.get_or_create(season_team_cup_tournament_ranking_id=ranking['id'],
                tournament_event=tevent)
        elif act_team is None and  cup_type == 'is_gc':
            act_team, cr = Team.objects.get_or_create(season_team_cup_championship_ranking_id=ranking['id'],
                tournament_event=tevent)
        elif act_team is None and  cup_type == 'is_sub':
            act_team, cr = Team.objects.get_or_create(season_team_sub_cup_tournament_ranking_id=ranking['id'],
                tournament_event=tevent)
        
        act_team.gbo_team = ranking['seasonTeam']['team']['id']
        act_team.season_team_id = ranking['seasonTeam']['id']
        act_team.season_team_cup_tournament_ranking_id = ranking['id']
        if cup_type == 'is_cup':
            act_team.season_team_cup_tournament_ranking_id = ranking['id']
            act_team.season_cup_tournament_id = tevent.tournament.season_cup_tournament_id
        elif cup_type == 'is_gc':
            act_team.season_team_cup_championship_ranking_id = ranking['id']
            act_team.season_cup_german_championship_id = tevent.tournament.season_cup_german_championship_id
        elif cup_type == 'is_sub':
            act_team.season_team_sub_cup_tournament_ranking_id = ranking['id']
        act_team.name = ranking['seasonTeam']['team']['name']
        act_team.abbreviation = ranking['seasonTeam']['team']['name_abbreviated']
        act_team.category = tevent.category
        act_team.is_dummy = False
        #team_bulk_list.append(act_team)
        act_team.save()

        season_team = None
        for st in teams_data:
            if st['id'] == act_team.season_team_id:
                season_team = st

        if season_team is None:
            return

        for season_player in season_team['seasonPlayers']:
            print('CheckPlayer:' + str(act_team.season_team_id) + ' ' + str(season_player['id']))
            cr = False
            act_player = next((x for x in players_list if x.tournament_event.id==tevent.id and x.season_team_id==act_team.season_team_id and x.season_player_id==season_player['id']), None)
            if act_player is None:
                #act_player, cr = Player.objects.get_or_create(tournament_event=tevent, season_team_id=act_team.season_team_id, season_player_id=season_player['id'])
                act_player = Player(tournament_event=tevent, season_team_id=act_team.season_team_id, season_player_id=season_player['id'])
                cr = True
            act_player.tournament_event = tevent
            act_player.team = act_team
            act_player.name = strip_accents(season_player['seasonSubject']['subject']['user']['family_name'])
            act_player.first_name = strip_accents(season_player['seasonSubject']['subject']['user']['name'])
            act_player.gbo_position = season_player['seasonSubject']['subject']['subjectLevel']['name']
            is_active = False
            for activeplayer in ranking['seasonPlayersInTournament']:
                if activeplayer['seasonPlayer']['id'] == season_player['id']:
                    is_active = True
            act_player.is_active = is_active
            act_player.number = season_player['number']
            act_player.season_team_id = act_team.season_team_id
            act_player.season_player_id = season_player['id']
            if cr:
                player_bulk_create_list.append(act_player)
            else:
                player_bulk_update_list.append(act_player)
            #act_player.save()
        
        # Coaches
        for season_coach in season_team['seasonCoaches']:
            cr = False
            act_coach = next((x for x in coaches_list if x.tournament_event.id==tevent.id and x.season_team_id==act_team.season_team_id and x.season_coach_id==season_coach['id']), None)
            if act_coach is None:
                act_coach = Coach(tournament_event=tevent, season_team_id=act_team.season_team_id, season_coach_id=season_coach['id'])
                cr = True
            act_coach.tournament_event = tevent
            act_coach.team = act_team
            act_coach.name = strip_accents(season_coach['seasonSubject']['subject']['user']['family_name'])
            act_coach.first_name = strip_accents(season_coach['seasonSubject']['subject']['user']['name'])
            act_coach.gbo_position = season_coach['seasonSubject']['subject']['subjectLevel']['name']
            act_coach.season_team_id = act_team.season_team_id
            act_coach.season_coach_id = season_coach['id']
            if cr:
                coach_bulk_create_list.append(act_coach)
            else:
                coach_bulk_update_list.append(act_coach)
            #act_coach.save()
        if len(player_bulk_create_list) > 0:
            Player.objects.bulk_create(player_bulk_create_list)
        if len(player_bulk_update_list) > 0:
            Player.objects.bulk_update(player_bulk_update_list, ("tournament_event", "team", "name", "first_name", "gbo_position", "is_active", "number","season_team_id", "season_player_id",))
        if len(coach_bulk_create_list) > 0:
            Coach.objects.bulk_create(coach_bulk_create_list)
        if len(coach_bulk_update_list) > 0:
            Coach.objects.bulk_update(coach_bulk_update_list, ("tournament_event", "team", "name", "first_name", "gbo_position","season_team_id", "season_coach_id",))
            
        #Coach.objects.bulk_update(coach_bulk_list)

    for dummy in my_dummy_team_data:
        if cup_type == 'is_cup':
            dummy.season_cup_tournament_id = season_cup_tourn_id_for_dummy
            continue
        if cup_type == 'is_gc':
            dummy.season_cup_german_championship_id = season_cup_tourn_id_for_dummy
            continue
        if cup_type == 'is_sub':
            continue
    if cup_type == 'is_cup':
        Team.objects.bulk_update(my_dummy_team_data, ("season_cup_tournament_id",))
    if cup_type == 'is_gc':
        Team.objects.bulk_update(my_dummy_team_data, ("season_cup_german_championship_id",))

    return

def strip_accents(text):

    try:
        text = str(bytes(text,'utf-8'), 'utf-8')
    except NameError: # unicode is a default on python 3 
        pass

    text = unicodedata.normalize('NFD', text)\
           .encode('ascii', 'ignore')\
           .decode("utf-8")

    return str(text)

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
            #tst.save()
        TeamStats.objects.bulk_update(tstats, ("number_of_played_games","game_points", "game_points_bonus", "ranking_points", "sets_win", "sets_loose", "points_made", "points_received"))

        #games = Game.objects.all().filter(tournament_event=ts.tournament_event,
        #                                  tournament_state=ts,
        #                                  gamestate='FINISHED')
        games = Game.objects.select_related("team_st_a__team", "team_st_b__team").filter(tournament_event=ts.tournament_event,
                                                                                    tournament_state=ts,
                                                                                    gamestate='FINISHED').all()
        games_bulk_list = []
        team_st_a_bulk_list = []
        team_st_b_bulk_list = []
        team_st_bulk_list = []
        num_finished_games = 0
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

            if iSetH == 0 and iSetA == 0:
                g.gamestate = GAMESTATE_CHOICES[0][0]
                games_bulk_list.append(g)
                continue

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

            ts_a_found = False
            ts_b_found = False
            for ts in team_st_bulk_list:
                if ts.id == teama_stats.id:
                    ts.number_of_played_games += teama_stats.number_of_played_games
                    ts.game_points += teama_stats.game_points
                    ts.ranking_points += teama_stats.ranking_points
                    ts.sets_win        += teama_stats.sets_win
                    ts.sets_loose      += teama_stats.sets_loose
                    ts.points_made     += teama_stats.points_made
                    ts.points_received += teama_stats.points_received
                    ts_a_found = True
                if ts.id == teamb_stats.id:
                    ts.number_of_played_games += teamb_stats.number_of_played_games
                    ts.game_points += teamb_stats.game_points
                    ts.ranking_points += teamb_stats.ranking_points
                    ts.sets_win        += teamb_stats.sets_win
                    ts.sets_loose      += teamb_stats.sets_loose
                    ts.points_made     += teamb_stats.points_made
                    ts.points_received += teamb_stats.points_received
                    ts_b_found = True
            if not ts_a_found:
                team_st_bulk_list.append(teama_stats)
            if not ts_b_found:
                team_st_bulk_list.append(teamb_stats)
            #teama_stats.save()
            #teamb_stats.save()
            g.gamingstate = 'Finished'
            g.calc_winner()
            games_bulk_list.append(g)
            num_finished_games = num_finished_games + 1
            #g.save()
        TeamStats.objects.bulk_update(team_st_bulk_list,("sets_win", "sets_loose", "points_made", "points_received", "game_points", "ranking_points", "number_of_played_games"))
        Game.objects.bulk_update(games_bulk_list,("gamingstate", "score_team_a_halftime_1", "score_team_a_halftime_2", "score_team_a_penalty", "score_team_b_halftime_1", "score_team_b_halftime_2", "score_team_b_penalty"))
        
        if not ts.direct_compare and num_finished_games > 0:
            teamstatsquery = _do_table_ordering(TeamStats.objects.filter(tournamentstate=ts))
            teamstats = teamstatsquery.all()
            max_val = teamstats.count()
            rank = 1
            for tstat in teamstats:
                tstat.ranking_points = tstat.ranking_points + max_val
                tstat.rank = rank
                rank = rank + 1
                max_val = max_val - 1
                #tstat.save()
            TeamStats.objects.bulk_update(teamstats, ("ranking_points","rank"))

        elif num_finished_games > 0:    
            check_direct_compare(ts)
            teamstatsquery = _do_table_ordering(TeamStats.objects.filter(tournamentstate=ts))
            teamstats = teamstatsquery.all()
            max_val = teamstats.count()
            rank = 1
            for tstat in teamstats:
                tstat.ranking_points = tstat.ranking_points + max_val
                tstat.rank = rank
                rank = rank + 1
                max_val = max_val - 1
                #tstat.save()
            TeamStats.objects.bulk_update(teamstats, ("ranking_points","rank"))
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
    if ts.direct_compare and Game.objects.all().filter(tournament_event=ts.tournament_event,
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
                games = Game.objects.all().filter(Q(team_st_a=teamst[0]) | Q(team_st_b=teamst[0]),
                                                  tournament_event=ts.tournament_event, tournament_state=ts)
                games = games.filter(Q(team_st_a=teamst[1]) | Q(team_st_b=teamst[1]),
                                     gamestate=GAMESTATE_CHOICES[2][1])
                if games.count() > 0:
                    teamstat = TeamStats.objects.get(id=get_game_winner(games.get()))
                    teamstat.game_points_bonus = 1
                    teamstat.save()

            elif teamst.count() > 2:
                print("Oh my goood")

def check_all_tournamentstate_finshed(tevent, states):
    #tstates = stages.tstates #TournamentState.objects.filter(tournament_event=tevent)
    ts_bulk_list = []
    for ts in states:
        games_played = 0
        for game in ts.games:
            if game.gamestate == GAMESTATE_CHOICES[2][1]:
                games_played = games_played + 1
        
        if games_played == len(ts.games):
            ts.is_finished = True
        else:
            ts.is_finished = False
        ts_bulk_list.append(ts)
        #ts.save(update_fields=['is_finished'])
    TournamentState.objects.bulk_update(ts_bulk_list, ("is_finished",))

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
        return game.winner_penalty

def getIntVal(val):
    if val is not None:
        return val
    else:
        return 0