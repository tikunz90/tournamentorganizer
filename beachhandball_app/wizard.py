from datetime import datetime
from django.db import transaction
from django.db.models.signals import post_save
from beachhandball_app import signals
from beachhandball_app.models.Team import Team, TeamStats
from beachhandball_app.models.Tournaments import TournamentStage, TournamentState, TournamentTeamTransition
from beachhandball_app.models.choices import COLOR_CHOICES, COLOR_CHOICES_DICT, TOURNAMENT_STAGE_TYPE_CHOICES, TOURNAMENT_STATE_CHOICES


def wizard_create_structure(tevent, structure_data):
    print('ENTER wizard_create_structure ' + str(datetime.now()))

    ts_final_ranking = TournamentState.objects.filter(tournament_event=tevent, is_final=True).first()
    tstats_final_ranking = TeamStats.objects.filter(tournament_event=tevent, tournamentstate=ts_final_ranking).all()
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
            state, team_stats, ttt = create_state_from_group(tstageGroup, tevent, TOURNAMENT_STATE_CHOICES[idx][1], gr, colorIdx, gr["name"], 'G' + str(gr["idx"]+1), hierarchy_counter)
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
    with transaction.atomic():
        for lvl in ko_data["level"]:
            if colorIdx > 4:
                colorIdx = 4
            if lvl["idx"] > 3:
                tstate_choice = 'ROUND_OF_' + str(2**lvl["idx"])
            elif lvl["idx"] == 3:
                tstate_choice = 'QUARTERFINALS'
            elif lvl["idx"] == 2:
                tstate_choice = 'SEMIFINALS'
            for gr in lvl["groups"]:
                if colorIdx > 4:
                    colorIdx = 4
                state, team_stats, team_transitions = create_state_from_group(tstageKO, tevent, tstate_choice, gr, colorIdx, lvl["header"] + ' ' + str(gr["idx"]), lvl["actNaming"] + ' ' + str(gr["idx"]), hierarchy_counter)
                if firstKoLevel:
                    # handle transitions from group
                    trans = structure_data["transitions"]["groups_to_ko"]["ko_grp_" + str(gr["idx"]-1)]
                    
                    for tstat in team_stats:
                        actTrans = [tr for tr in trans if tr["target_rank"] == tstat.rank][0]
                        actTTT = [tr for tr in tttGroup[actTrans["origin_group_id"]] if tr.origin_rank == actTrans["origin_rank"]][0]
                        actTTT.target_ts_id = state
                        tstat.name_table = '{}. {}'.format(actTTT.origin_rank, actTTT.origin_ts_id)
                        if tstat.team.is_dummy is True:
                            tstat.team.name = '{}. {}'.format(actTTT.origin_rank, actTTT.origin_ts_id)
                            tstat.team.abbreviation = '{}. {}'.format(actTTT.origin_rank, actTTT.origin_ts_id.abbreviation)
                        tstat.team.save()
                        tstat.save()
                        actTTT.save()

                    
                #state.save()
                colorIdx += 1
            hierarchy_counter += 1
            if firstKoLevel:
                firstKoLevel = False
            colorIdx = 0

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
            if colorIdx > 4:
                colorIdx = 4
            for gr in lvl["groups"]:
                create_state_from_group(tstagePlace, tevent, 'LOOSER_ROUND', gr, colorIdx, gr["name"], gr["name"], hierarchy_counter)
                colorIdx += 1

            for sublevel in lvl["sublevel"]:
                tstatesPlace = tstatesPlace + create_states_sublevel(tevent, tstagePlace, sublevel, hierarchy_counter);
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
        state, ts, ttt = create_state_from_group(tstageFinal, tevent, 'FINAL', gr, 6, "Final", "F", 100)

        trans = [t["transition"] for t in gr["teams"] if t["transition"]["origin_rank"] == 1 and t["transition"]["target_group_id"] == 999][0]
        tstat_rank = [t for t in tstats_final_ranking if t.rank_initial == 1][0]
        
        tttWinner = TournamentTeamTransition(tournament_event=tevent,
                                                origin_ts_id=state,
                                                origin_rank=1,
                                                target_ts_id=ts_final_ranking,
                                                target_rank=trans["target_rank"])
        tstat_rank.name_table = '{}. {}'.format(tttWinner.origin_rank, tttWinner.origin_ts_id)
        if tstat_rank.team.is_dummy is True:
            tstat_rank.team.name = '{}. {}'.format(tttWinner.origin_rank, tttWinner.origin_ts_id)
            tstat_rank.team.abbreviation = '{}. {}'.format(tttWinner.origin_rank, tttWinner.origin_ts_id.abbreviation)
            teams_final_ranking.append(tstat_rank.team)

        trans = [t["transition"] for t in gr["teams"] if t["transition"]["origin_rank"] == 2 and t["transition"]["target_group_id"] == 999][0]
        tstat_rank = [t for t in tstats_final_ranking if t.rank_initial == 2][0]
        ttt2nd = TournamentTeamTransition(tournament_event=tevent,
                                                origin_ts_id=state,
                                                origin_rank=2,
                                                target_ts_id=ts_final_ranking,
                                                target_rank=2)
        tstat_rank.name_table = '{}. {}'.format(tttWinner.origin_rank, tttWinner.origin_ts_id)
        if tstat_rank.team.is_dummy is True:
            tstat_rank.team.name = '{}. {}'.format(tttWinner.origin_rank, tttWinner.origin_ts_id)
            tstat_rank.team.abbreviation = '{}. {}'.format(tttWinner.origin_rank, tttWinner.origin_ts_id.abbreviation)
            teams_final_ranking.append(tstat_rank.team)

    transitions.append(tttWinner)
    transitions.append(ttt2nd)

    #Team.objects.bulk_update(teams_final_ranking, ['name', 'abbreviation'])
    #TeamStats.objects.bulk_update(tstats_final_ranking, ['name_table'])
    #TournamentTeamTransition.objects.bulk_create(transitions)
    
    post_save.connect(signals.create_new_tournamentstate, sender=TournamentState)
    post_save.connect(signals.teamstat_changed, sender=TeamStats)

    print('EXIT wizard_create_structure ' + str(datetime.now()))
    return 0

def create_states_sublevel(tevent, tstage, sublevel, hierarchy):
    states = []
    colorIdx = 0
    
    for gr in sublevel["groups"]:
        if colorIdx > 4:
            colorIdx = 4
        create_state_from_group(tstage, tevent, 'LOOSER_ROUND', gr, colorIdx, gr["name"], gr["name"], hierarchy)
        colorIdx += 1
    for sublevel in sublevel["sublevel"]:
        states = states + create_states_sublevel(tevent, tstage, sublevel, hierarchy);
    
    return states

def create_state_from_group(stage, tevent, tstate_choice, gr, colorIdx, name, abbr, hierarchy):
    state, cr = TournamentState.objects.get_or_create(tournament_event=tevent,
                tournament_state=tstate_choice,
                tournament_stage=stage,
                index=gr["idx"]-1,
                name=name,
                abbreviation=abbr,
                hierarchy=hierarchy,
                max_number_teams=len(gr["teams"]), 
                color=COLOR_CHOICES[colorIdx][0])

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