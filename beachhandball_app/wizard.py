from datetime import datetime
from django.db import transaction
from django.db.models.signals import post_save
from authentication.models import ScoreBoardUser
from django.contrib.auth.models import User, Group
from beachhandball_app import signals
from beachhandball_app.models.Game import Game
from beachhandball_app.models.Team import Team, TeamStats
from beachhandball_app.models.Tournaments import Court, TournamentStage, TournamentState, TournamentTeamTransition
from beachhandball_app.models.choices import COLOR_CHOICES, COLOR_CHOICES_DICT, KNOCKOUT_NAMES, ROUND_TYPES, TOURNAMENT_STAGE_TYPE_CHOICES, TOURNAMENT_STATE_CHOICES


def wizard_create_structure(tevent, structure_data):
    print('ENTER wizard_create_structure ' + str(datetime.now()))

    ts_final_ranking, cr = TournamentState.objects.get_or_create(tournament_event=tevent,
        tournament_state=TOURNAMENT_STATE_CHOICES[-1][1],
        name='Final Ranking',
        abbreviation='FR',
        hierarchy=999,
        max_number_teams=int(structure_data['max_num_teams']),
        is_final=True)
    tstats_final_ranking = TeamStats.objects.filter(tournament_event=tevent, tournamentstate=ts_final_ranking).all()
    ts_final_ranking.round_type = ROUND_TYPES.RANKING
    ts_final_ranking.save()
    teams_final_ranking = []
    transitions = []
    hierarchy_counter = 0
    ####################################################
    # GROUPSTAGE
    ####################################################
    group_data = structure_data["groups"]
    tstageGroup, cr = TournamentStage.objects.get_or_create(tournament_event=tevent, name='Groups')
    tstageGroup.short_name = 'G'
    tstageGroup.tournament_stage = TOURNAMENT_STAGE_TYPE_CHOICES[0][1]
    tstageGroup.order = 0
    tstageGroup.save()
    tstatesGroup = []

    tttGroup = {}
    colorIdx = 0

    post_save.disconnect(signals.create_new_tournamentstate, sender=TournamentState)
    post_save.disconnect(signals.teamstat_changed, sender=TeamStats)
    print('START GROUPS ' + str(datetime.now()))
    
    with transaction.atomic():
        for gr in group_data["items"]:
            idx = gr["idx"]
            if idx > 5:
                idx = 5
                colorIdx = 5
            state, team_stats, ttt = create_state_from_group(tstageGroup, tevent, TOURNAMENT_STATE_CHOICES[idx][1], gr, colorIdx, gr["name"], 'G' + str(gr["idx"]+1), hierarchy_counter, ROUND_TYPES.GROUP)
            tttGroup[idx] = ttt
            colorIdx += 1
    
    print('FINISH GROUPS ' + str(datetime.now()))
    hierarchy_counter += 1
    ####################################################
    # KNOCKOUT
    ####################################################
    ko_data = structure_data["ko"]
    tstageKO, cr = TournamentStage.objects.get_or_create(tournament_event=tevent, name='Knockout')
    tstageKO.short_name = 'KO'
    tstageKO.tournament_stage = TOURNAMENT_STAGE_TYPE_CHOICES[2][1]
    tstageKO.order = 1
    tstageKO.save()
    tstatesKO = []

    colorIdx = 0
    firstKoLevel = True
    last_trans_from_wizard = []
    tttLastState = {}
    tttNewState = {}
    tttToPlace = {}
    tttToFinal = {}
    transToFinal = []
    with transaction.atomic():
        for lvl in ko_data["level"]:
            round_type = 'ROUND_' + str(2**lvl["idx"])
            if colorIdx > 4:
                colorIdx = 4
            if lvl["idx"] > 3:
                tstate_choice = 'ROUND_OF_' + str(2**lvl["idx"])
            elif lvl["idx"] == 3:
                tstate_choice = 'QUARTERFINALS'
            elif lvl["idx"] == 2:
                tstate_choice = 'SEMIFINALS'
            tttToPlace[lvl["idx"]] = []
            for gr in lvl["groups"]:
                if colorIdx > 4:
                    colorIdx = 4
                state, team_stats, tttAct = create_state_from_group(tstageKO, tevent, tstate_choice, gr, colorIdx, lvl["header"] + ' ' + str(gr["idx"]), lvl["actNaming"] + ' ' + str(gr["idx"]), hierarchy_counter, round_type)
                
                if firstKoLevel:
                    # handle transitions from group
                    tttTemp = tttGroup
                    trans = structure_data["transitions"]["groups_to_ko"]["ko_grp_" + str(gr["idx"]-1)]
                else:
                    tttTemp = tttLastState
                    trans =[tr for tr in last_trans_from_wizard if tr["origin_rank"] == 1 and tr["target_group_id"] == gr["idx"]-1]
                
                handle_transitions_ko(state, trans, team_stats, tttTemp)
                tttToPlace[lvl["idx"]] += [tr for tr in tttAct if tr.origin_rank == 2]
                tttNewState[gr["idx"]-1] = tttAct
                #state.save()
                colorIdx += 1
            last_trans_from_wizard = lvl["transitions"]
            tttLastState = tttNewState
            hierarchy_counter += 1
            if firstKoLevel:
                firstKoLevel = False
            colorIdx = 0
    tttToFinal = tttLastState
    transToFinal = last_trans_from_wizard

    ####################################################
    # PLACEMENT
    ####################################################
    hierarchy_counter = 500
    pl_data = structure_data["placement"]
    tstagePlace, cr = TournamentStage.objects.get_or_create(tournament_event=tevent, name='Placement')
    tstagePlace.short_name = 'P'
    tstagePlace.tournament_stage = TOURNAMENT_STAGE_TYPE_CHOICES[3][1]
    tstagePlace.order = 2
    tstagePlace.save()
    tstatesPlace = []

    colorIdx = 0
    with transaction.atomic():
        for lvl in pl_data["level"]:
            ko_name = KNOCKOUT_NAMES[2**(lvl["idx"]+1)]
            if colorIdx > 4:
                colorIdx = 4
            tttToSubLevel = []
            for gr in lvl["groups"]:
                state, team_stats, tttAct = create_state_from_group(tstagePlace, tevent, 'LOOSER_ROUND', gr, colorIdx, gr["name"], gr["name"], hierarchy_counter, ROUND_TYPES.PLAYOFF)

                trans = [ tr for tr in structure_data["transitions"]["ko_to_pl"][ko_name]["items"] if tr["target_group_id"] == gr["idx"]-1]
                tttTemp = tttToPlace[lvl["idx"]+1]
                    
                handle_transitions_pl(state, trans, team_stats, tttTemp)
                tttToSubLevel += tttAct
                if len(lvl["sublevel"]) == 0:
                    handle_transitions_ranking(ts_final_ranking, tstats_final_ranking, tttAct)
                colorIdx += 1
            sublevel_counter = 0
            for sublevel in lvl["sublevel"]:
                if sublevel_counter == 0:
                    trans = lvl["transitions_l"]
                else:
                    trans = lvl["transitions_w"]
                tstatesPlace = tstatesPlace + create_states_sublevel(tevent, tstagePlace, sublevel, hierarchy_counter, ts_final_ranking, tstats_final_ranking, tttToSubLevel, trans);
                sublevel_counter += 1
            hierarchy_counter += 1
            colorIdx += 1

    ####################################################
    # FINALS
    ####################################################
    final_data = structure_data["finals"]
    tstageFinal, cr = TournamentStage.objects.get_or_create(tournament_event=tevent, name='Final')
    tstageFinal.short_name = 'F'
    tstageFinal.tournament_stage = TOURNAMENT_STAGE_TYPE_CHOICES[4][1]
    tstageFinal.order = 3
    tstageFinal.save()
    for gr in final_data["groups"]:
        state, ts, ttt = create_state_from_group(tstageFinal, tevent, 'FINAL', gr, 6, "Final", "F", 100, ROUND_TYPES.ROUND_2)

        handle_transitions_ko(state, transToFinal, ts, tttToFinal)

        #trans = [t["transition"] for t in gr["teams"] if t["transition"]["origin_rank"] == 1 and t["transition"]["target_group_id"] == 999][0]
        handle_transitions_ranking(ts_final_ranking, tstats_final_ranking, ttt)


    #Team.objects.bulk_update(teams_final_ranking, ['name', 'abbreviation'])
    #TeamStats.objects.bulk_update(tstats_final_ranking, ['name_table'])
    #TournamentTeamTransition.objects.bulk_create(transitions)
    
    post_save.connect(signals.create_new_tournamentstate, sender=TournamentState)
    post_save.connect(signals.teamstat_changed, sender=TeamStats)

    print('EXIT wizard_create_structure ' + str(datetime.now()))
    return 0

def create_states_sublevel(tevent, tstage, sublevel, hierarchy, ts_final_ranking, tstats_final_ranking, tttParent, transitions):
    states = []
    colorIdx = 0
    tttSubParent = []
    for gr in sublevel["groups"]:
        if colorIdx > 4:
            colorIdx = 4
        state, team_stats, tttAct = create_state_from_group(tstage, tevent, 'LOOSER_ROUND', gr, colorIdx, gr["name"], gr["name"], hierarchy, ROUND_TYPES.PLAYOFF)
        
        trans = [ tr for tr in transitions if tr["target_group_id"] == gr["idx"]-1]
        tttTemp = tttParent
            
        handle_transitions_pl(state, trans, team_stats, tttTemp)
        colorIdx += 1
        if len(sublevel["sublevel"]) == 0:
            handle_transitions_ranking(ts_final_ranking, tstats_final_ranking, tttAct)
        tttSubParent += tttAct
    
    sublevel_counter = 0
    for sub in sublevel["sublevel"]:
        if sublevel_counter == 0:
            trans = sublevel["transitions_l"]
        else:
            trans = sublevel["transitions_w"]
        states = states + create_states_sublevel(tevent, tstage, sub, hierarchy, ts_final_ranking, tstats_final_ranking, tttSubParent, trans);
        sublevel_counter += 1
    
    return states

def create_state_from_group(stage, tevent, tstate_choice, gr, colorIdx, name, abbr, hierarchy, round_type):
    state, cr = TournamentState.objects.get_or_create(tournament_event=tevent,
                tournament_state=tstate_choice,
                tournament_stage=stage,
                index=gr["idx"]-1,
                name=name,
                abbreviation=abbr,
                hierarchy=hierarchy,
                max_number_teams=len(gr["teams"]), 
                color=COLOR_CHOICES[colorIdx][0],
                direct_compare=True,
                round_type=round_type,
                order=gr["idx"])

    #for i in range(1, state.max_number_teams+1):
    team_stats = []
    team_transitions = []
    i = 1
    for t in gr["teams"]:
        new_dummy_team, cr = Team.objects.get_or_create(tournament_event=state.tournament_event,
                            tournamentstate=state,
                            name="{}. {}".format(i, state),
                            abbreviation="{}.{}".format(i, state.abbreviation),
                            category=state.tournament_event.category,
                            season_cup_tournament_id=state.tournament_event.season_cup_tournament_id,
                            is_dummy=True)
        act_team_st, cr = TeamStats.objects.get_or_create(tournament_event=state.tournament_event,
                        tournamentstate=state,
                        team=new_dummy_team,
                        rank_initial=i,
                        rank=i)
        ttt, cr = TournamentTeamTransition.objects.get_or_create(tournament_event=tevent,
                                                origin_ts_id=state,
                                                origin_rank=i,
                                                target_rank=t["transition"]["target_rank"])
        team_stats.append(act_team_st)
        team_transitions.append(ttt)
        i += 1
    return (state, team_stats, team_transitions)

def handle_transitions_ko(state, trans, team_stats, tttLastState):
                   
    for tstat in team_stats:
        actTrans = [tr for tr in trans if tr["target_rank"] == tstat.rank][0]
        actTTT = [tr for tr in tttLastState[actTrans["origin_group_id"]] if tr.origin_rank == actTrans["origin_rank"]][0]
        actTTT.target_ts_id = state
        tstat.name_table = '{}. {}'.format(actTTT.origin_rank, actTTT.origin_ts_id)
        if tstat.team.is_dummy is True:
            tstat.team.name = '{}. {}'.format(actTTT.origin_rank, actTTT.origin_ts_id)
            tstat.team.abbreviation = '{}. {}'.format(actTTT.origin_rank, actTTT.origin_ts_id.abbreviation)
        tstat.team.save()
        tstat.save()
        actTTT.save()

def handle_transitions_pl(state, trans, team_stats, tttLastState):
                   
    for tstat in team_stats:
        actTrans = [tr for tr in trans if tr["target_rank"] == tstat.rank][0]
        actTTT = [tr for tr in tttLastState if tr.origin_rank == actTrans["origin_rank"] and (actTrans["origin_group_name"] in tr.origin_ts_id.name or actTrans["origin_group_name"] in tr.origin_ts_id.abbreviation)][0]
        actTTT.target_ts_id = state
        tstat.name_table = '{}. {}'.format(actTTT.origin_rank, actTTT.origin_ts_id)
        if tstat.team.is_dummy is True:
            tstat.team.name = '{}. {}'.format(actTTT.origin_rank, actTTT.origin_ts_id)
            tstat.team.abbreviation = '{}. {}'.format(actTTT.origin_rank, actTTT.origin_ts_id.abbreviation)
        tstat.team.save()
        tstat.save()
        actTTT.save()

def handle_transitions_ranking(ts_final_ranking, tstats_final_ranking, ttt):
    #trans = [t["transition"] for t in gr["teams"] if t["transition"]["origin_rank"] == 1 and t["transition"]["target_group_id"] == 999][0]
    tstat_rank = [t for t in tstats_final_ranking if t.rank_initial == 1][0]
    
    tttWinner = [t for t in ttt if t.origin_rank == 1][0]
    tttWinner.target_ts_id = ts_final_ranking
    tstat_rank.name_table = '{}. {}'.format(tttWinner.origin_rank, tttWinner.origin_ts_id)
    if tstat_rank.team.is_dummy is True:
        tstat_rank.team.name = '{}. {}'.format(tttWinner.origin_rank, tttWinner.origin_ts_id)
        tstat_rank.team.abbreviation = '{}. {}'.format(tttWinner.origin_rank, tttWinner.origin_ts_id.abbreviation)
    tttWinner.save()
    tstat_rank.team.save()
    tstat_rank.save()
    #trans = [t["transition"] for t in gr["teams"] if t["transition"]["origin_rank"] == 2 and t["transition"]["target_group_id"] == 999][0]
    tstat_rank = [t for t in tstats_final_ranking if t.rank_initial == 2][0]
    ttt2nd = [t for t in ttt if t.origin_rank == 2][0]
    ttt2nd.target_ts_id = ts_final_ranking
    tstat_rank.name_table = '{}. {}'.format(ttt2nd.origin_rank, ttt2nd.origin_ts_id)
    if tstat_rank.team.is_dummy is True:
        tstat_rank.team.name = '{}. {}'.format(ttt2nd.origin_rank, ttt2nd.origin_ts_id)
        tstat_rank.team.abbreviation = '{}. {}'.format(ttt2nd.origin_rank, ttt2nd.origin_ts_id.abbreviation)
    ttt2nd.save()
    tstat_rank.team.save()
    tstat_rank.save()



def wizard_create_gameplan(tourn, gameplan_data, num_courts):
    courts = {}
    for i in range(1, int(num_courts)+1):
        court, cr = Court.objects.get_or_create(tournament=tourn, name='C' + str(i), number=i)
        if cr is True:
            user = User.objects.create_user(str(tourn.id) + '_C' + str(i), 'dummy@mail.de', 'Start1234')
            user.first_name = 'Court'
            user.last_name = 'C' + str(i)
            user.save()
            sbUser = ScoreBoardUser(user=user, court=court)
            sbUser.save()
            
            sb_group, cr = Group.objects.get_or_create(name='scoreboard')
            sb_group.user_set.add(user)
            sb_group.save()
        else:
            sbUser, cr = ScoreBoardUser.objects.get_or_create(court=court)
            if cr is True:
                user = User.objects.create_user(str(tourn.id) + '_C' + str(i), 'dummy@mail.de', 'Start1234')
                user.first_name = 'Court'
                user.last_name = 'C' + str(i)
                user.save()
                sbUser.user = user
                sbUser.save()
                sb_group, cr = Group.objects.get_or_create(name='scoreboard')
                sb_group.user_set.add(user)
                sb_group.save()
                
        courts[i] = court
    games = []
    game_counter = 1
    for g in gameplan_data:
        actCourt = courts[int(g['court'][1:])]
        game_obj = Game(tournament=tourn,
            tournament_event_id=g['tournament_event_id'],
            tournament_state_id=g['tournament_state_id'],
            starttime=datetime.fromtimestamp(g['starttime']),
            team_a_id=g['team_a_id'],
            team_b_id=g['team_b_id'],
            team_st_a_id=g['team_st_a_id'],
            team_st_b_id=g['team_st_b_id'],
            court=actCourt,
            gamestate='APPENDING',
            scouting_state='APPENDING',
            gamingstate='Ready',
            id_counter=game_counter)
        game_counter += 1
        games.append(game_obj)
    Game.objects.bulk_create(games)
    return game_counter