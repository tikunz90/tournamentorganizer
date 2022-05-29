from beachhandball_app.models.Tournaments import TournamentStage, TournamentState, TournamentTeamTransition
from beachhandball_app.models.choices import COLOR_CHOICES, TOURNAMENT_STAGE_TYPE_CHOICES, TOURNAMENT_STATE_CHOICES


def wizard_create_structure(tevent, structure_data):
    print('ENTER wizard_create_structure')

    # GROUPSTAGE
    group_data = structure_data["groups"]
    tstageGroup, cr = TournamentStage.objects.get_or_create(tournament_event=tevent, name='Groups')
    tstageGroup.short_name = 'G'
    tstageGroup.tournament_stage = TOURNAMENT_STAGE_TYPE_CHOICES[0][1]
    tstageGroup.order = 0
    tstageGroup.save()
    tstatesGroup = []
    colorIdx = 0
    for gr in group_data["items"]:
        idx = gr["idx"]
        if idx > 5:
            idx = 5
        state, cr = TournamentState.objects.get_or_create(tournament_event=tevent,
            tournament_state=TOURNAMENT_STATE_CHOICES[idx][1],
            tournament_stage=tstageGroup,
            name=gr["name"],
            abbreviation='G' + str(gr["idx"]+1),
            max_number_teams=len(gr["teams"]), 
            color=COLOR_CHOICES[colorIdx][0])
        colorIdx += 1
        state.save()
        tstatesGroup.append(state)


    # KNOCKOUT
    ko_data = structure_data["ko"]
    tstageKO, cr = TournamentStage.objects.get_or_create(tournament_event=tevent, name='Knockout')
    tstageKO.short_name = 'KO'
    tstageKO.tournament_stage = TOURNAMENT_STAGE_TYPE_CHOICES[2][1]
    tstageKO.order = 1
    tstageKO.save()

    colorIdx = 0
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
            state, cr = TournamentState.objects.get_or_create(tournament_event=tevent,
            tournament_state=tstate_choice,
            tournament_stage=tstageKO,
            name=lvl["header"] + ' ' + str(gr["idx"]),
            abbreviation=gr["name"],
            max_number_teams=len(gr["teams"]), 
            color=COLOR_CHOICES[colorIdx][0])
            state.save()
        colorIdx += 1

    # PLACEMENT
    pl_data = structure_data["placement"]
    tstagePlace, cr = TournamentStage.objects.get_or_create(tournament_event=tevent, name='Placement')
    tstagePlace.short_name = 'P'
    tstagePlace.tournament_stage = TOURNAMENT_STAGE_TYPE_CHOICES[3][1]
    tstagePlace.order = 2
    tstagePlace.save()

    colorIdx = 0
    for lvl in pl_data["level"]:
        if colorIdx > 4:
            colorIdx = 4
        for gr in lvl["groups"]:
            state, cr = TournamentState.objects.get_or_create(tournament_event=tevent,
                tournament_state='LOOSER_ROUND',
                tournament_stage=tstagePlace,
                name=gr["name"],
                abbreviation=gr["name"],
                max_number_teams=len(gr["teams"]), 
                color=COLOR_CHOICES[colorIdx][0])
            state.save()
        colorIdx += 1

    # FINALS
    final_data = structure_data["finals"]
    tstageFinal, cr = TournamentStage.objects.get_or_create(tournament_event=tevent, name='Final')
    tstageFinal.short_name = 'F'
    tstageFinal.tournament_stage = TOURNAMENT_STAGE_TYPE_CHOICES[4][1]
    tstageFinal.order = 3
    tstageFinal.save()

    #tttWinner, cr = TournamentTeamTransition.objects.get_or_create(tournament_event=tevent,
    #origin_ts_id=1,
    #origin_rank=1,
    #target_ts_id=1,
    #target_rank=1)
#
    #ttt2nd, cr = TournamentTeamTransition.objects.get_or_create(tournament_event=tevent,
    #origin_ts_id=1,
    #origin_rank=2,
    #target_ts_id=1,
    #target_rank=2)
    
    return 0
