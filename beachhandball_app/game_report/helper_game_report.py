from django.db.models.query import Prefetch
from openpyxl.cell.cell import TYPE_STRING
from beachhandball_app.models.Tournaments import Tournament, TournamentSettings
from beachhandball_app.models.choices import CATEGORY_CHOICES
from beachhandball_app.models.Game import Game
from beachhandball_app.models.Player import Player, PlayerStats

import os
from shutil import copyfile

from openpyxl import load_workbook
from openpyxl.drawing.image import Image

from django.conf import settings

def create_pregame_report_excel(game):
    print('ENTER create_report_excel')
    print('game_report DIR: ' + settings.GAME_REPORT_DIR)
    tsettings = TournamentSettings.objects.get(tournament=game.tournament)
    if not tsettings.game_report_template:
        return ('', '')

    gr_template = tsettings.game_report_template
    filename_template = gr_template.filename #
    filename = 'PreGame_' + game.tournament_event.category.abbreviation + str(game.id_counter) + '.xlsx'

    fullfilepath_template = os.path.join(settings.GAME_REPORT_DIR, filename_template)
    fullfilepath_report = os.path.join(settings.GAME_REPORT_DIR, filename)
    # copy template
    copyfile(fullfilepath_template, fullfilepath_report)

    if os.path.isfile(fullfilepath_report):
        print('file exists')
        wb = load_workbook(filename = fullfilepath_report)
        ws = wb.active
        #img = Image(os.path.join(settings.GAME_REPORT_DIR,'dhb_logo.png'))
        #ws_copy = wb.copy_worksheet(ws)
        #ws.add_image(img, 'T1')
        # game id
        tsettings = TournamentSettings.objects.get(tournament=game.tournament_event.tournament)
        tstage = game.tournament_state.tournament_stage
        ws[gr_template.cell_game_id] = game.tournament_event.category.abbreviation + str(game.id_counter)
        
        # category
        if game.tournament_event.category.abbreviation == 'M': # CATEGORY_CHOICES[0][0]:
            ws[gr_template.cell_category_men] = 'X'
        elif game.tournament_event.category.abbreviation == 'W': # CATEGORY_CHOICES[1][0]:
            ws[gr_template.cell_category_women] = 'X'

        # court
        ws[gr_template.cell_court_number] = game.court.number

        # team names
        ws[gr_template.cell_team_a_name] = game.team_st_a.team.name
        ws[gr_template.cell_team_b_name] = game.team_st_b.team.name

        # ref names
        if game.ref_a is not None:
            ws[gr_template.cell_ref_a_name] = game.ref_a.name + ', ' + game.ref_a.first_name
        if game.ref_b is not None:
            ws[gr_template.cell_ref_b_name] = game.ref_b.name + ', ' + game.ref_b.first_name 

        # stage
        if tstage is not None:
            if tstage.tournament_stage == 'GROUP_STAGE':
                ws[gr_template.cell_group_stage] = 'X'
            if tstage.tournament_stage == 'KNOCKOUT_STAGE' or tstage.tournament_stage == 'FINAL' or tstage.tournament_stage == 'PLAYOFF_STAGE':
                ws[gr_template.cell_knockout_stage] = 'X'

        # Date and Time
        date = game.starttime.strftime("%d.%m.%Y")
        time = game.starttime.strftime("%H:%M")
        ws[gr_template.cell_date] = date
        ws[gr_template.cell_time] = time
        max_num_player = tsettings.amount_players_report
        row_start_a = gr_template.team_a_start_row
        act_player_counter = 1
        for player in game.team_st_a.team.player_set.order_by('number').all():
            if act_player_counter > max_num_player:
                break
            if not player.is_active:
                continue
            ws[gr_template.team_a_player_number_col+str(row_start_a)]=player.number
            ws[gr_template.team_a_player_name_col+str(row_start_a)]=player.name + ", " + player.first_name
            act_player_counter = act_player_counter + 1
            row_start_a = row_start_a + 1
        row_start_b = gr_template.team_b_start_row
        act_player_counter = 1
        for player in game.team_st_b.team.player_set.order_by('number').all():
            if act_player_counter > max_num_player:
                break
            if not player.is_active:
                continue
            ws[gr_template.team_b_player_number_col+str(row_start_b)]=player.number
            ws[gr_template.team_b_player_name_col+str(row_start_b)]=player.name + ", " + player.first_name
            act_player_counter = act_player_counter + 1
            row_start_b = row_start_b + 1
        max_num_coaches = gr_template.max_num_coaches
        row_start_coach_a = gr_template.team_a_start_row_coaches
        for coach in game.team_st_a.team.coach_set.all()[:max_num_coaches]:
            ws[gr_template.team_a_coach_name_col +str(row_start_coach_a)]=coach.name + ", " + coach.first_name
            row_start_coach_a = row_start_coach_a + 1
        row_start_coach_b = gr_template.team_b_start_row_coaches
        for coach in game.team_st_b.team.coach_set.all()[:max_num_coaches]:
            ws[gr_template.team_b_coach_name_col+str(row_start_coach_b)]=coach.name + ", " + coach.first_name
            row_start_coach_b = row_start_coach_b + 1

        wb.save(fullfilepath_report)

        return fullfilepath_report, filename
    return ('', '')


def create_all_tstate_pregame_report_excel(tstate):
    print('ENTER create_report_excel')
    print('game_report DIR: ' + settings.GAME_REPORT_DIR)

    tsettings = TournamentSettings.objects.get(tournament=tstate.tournament)
    if not tsettings.game_report_template:
        return ''
    
    gr_template = tsettings.game_report_template

    filename_template = tsettings.game_report_template.filename
    filename = 'PreGame_ALL_'  + str(tstate.name) + '.xlsx'

    fullfilepath_template = os.path.join(settings.GAME_REPORT_DIR, filename_template)
    fullfilepath_report = os.path.join(settings.GAME_REPORT_DIR, filename)
    # copy template
    copyfile(fullfilepath_template, fullfilepath_report)

    if os.path.isfile(fullfilepath_report):
        print('file exists')
        tsettings = TournamentSettings.objects.get(tournament=tstate.tournament_event.tournament)
        games = Game.objects.filter(tournament_state=tstate)
        tstage = tstate.tournament_stage
        wb = load_workbook(filename = fullfilepath_report)
        ws_origin = wb.active
        #img = Image(os.path.join(settings.GAME_REPORT_DIR,'dhb_logo.png'))
        for game in games:
            
            ws_game = wb.copy_worksheet(ws_origin)
            ws_game.title = game.tournament_event.category.abbreviation + str(game.id)
            # game id
            ws_game[gr_template.cell_game_id] = game.tournament_event.category.abbreviation + str(game.id)
            
            # category
            if game.tournament_event.category.abbreviation == 'M': # CATEGORY_CHOICES[0][0]:
                ws_game[gr_template.cell_category_men] = 'X'
            elif game.tournament_event.category.abbreviation == 'W': # CATEGORY_CHOICES[1][0]:
                ws_game[gr_template.cell_category_women] = 'X'

            # court
            ws_game[gr_template.cell_court_number] = game.court.number

            # team names
            ws_game[gr_template.cell_team_a_name] = game.team_st_a.team.name
            ws_game[gr_template.cell_team_b_name] = game.team_st_b.team.name

            # ref names
            if game.ref_a is not None:
                ws_game[gr_template.cell_ref_a_name] = game.ref_a.name + ', ' + game.ref_a.first_name
            if game.ref_b is not None:
                ws_game[gr_template.cell_ref_b_name] = game.ref_b.name + ', ' + game.ref_b.first_name 

            # stage
            if tstage is not None:
                if tstage.tournament_stage == 'GROUP_STAGE':
                    ws_game[gr_template.cell_group_stage] = 'X'
                if tstage.tournament_stage == 'KNOCKOUT_STAGE' or tstage.tournament_stage == 'FINAL' or tstage.tournament_stage == 'PLAYOFF_STAGE':
                    ws_game[gr_template.cell_knockout_stage] = 'X'

            # Date and Time
            date = game.starttime.strftime("%d.%m.%Y")
            time = game.starttime.strftime("%H:%M")
            ws_game[gr_template.cell_date] = date
            ws_game[gr_template.cell_time] = time
            max_num_player = tsettings.amount_players_report
            row_start_a = gr_template.team_a_start_row
            act_player_counter = 1
            for player in game.team_st_a.team.player_set.all():
                if act_player_counter > max_num_player:
                    break
                if not player.is_active:
                    continue
                ws_game[gr_template.team_a_player_number_col+str(row_start_a)]=player.number
                ws_game[gr_template.team_a_player_name_col  +str(row_start_a)]=player.name + ", " + player.first_name
                act_player_counter = act_player_counter + 1
                row_start_a = row_start_a + 1
            row_start_b = gr_template.team_b_start_row
            act_player_counter = 1
            for player in game.team_st_b.team.player_set.all():
                if act_player_counter > max_num_player:
                    break
                if not player.is_active:
                    continue
                ws_game[gr_template.team_b_player_number_col+str(row_start_b)]=player.number
                ws_game[gr_template.team_b_player_name_col  +str(row_start_b)]=player.name + ", " + player.first_name
                act_player_counter = act_player_counter + 1
                row_start_b = row_start_b + 1
            max_num_coaches = gr_template.max_num_coaches
            row_start_coach_a = gr_template.team_a_start_row_coaches
            for coach in game.team_st_a.team.coach_set.all()[:max_num_coaches]:
                ws_game[gr_template.team_a_coach_name_col+str(row_start_coach_a)]=coach.name + ", " + coach.first_name
                row_start_coach_a = row_start_coach_a + 1
            row_start_coach_b = gr_template.team_b_start_row_coaches
            for coach in game.team_st_b.team.coach_set.all()[:max_num_coaches]:
                ws_game[gr_template.team_b_coach_name_col+str(row_start_coach_b)]=coach.name + ", " + coach.first_name
                row_start_coach_b = row_start_coach_b + 1
        wb.remove_sheet(ws_origin)
        wb.save(fullfilepath_report)

        return fullfilepath_report, filename
    return ''

def import_game_report_excel(game):
    print('ENTER import_game_report_excel')
    print('game_report DIR: ' + settings.GAME_REPORT_DIR)
    tourn = Tournament.objects.get(id=28)
    tsettings = TournamentSettings.objects.get(tournament=tourn)
    if not tsettings.game_report_template:
        return ''

    gr_template = tsettings.game_report_template


def import_single_game_report(game, filename):
    print('ENTER import_single_game_report ' + filename)

def import_game_report_excel():
    print('ENTER import_game_report_excel')
    print('game_report DIR: ' + settings.GAME_REPORT_DIR)


    files = [f for f in os.listdir(os.path.join(settings.GAME_REPORT_DIR, 'post')) if f.endswith('.xlsx')]

    tourn = Tournament.objects.get(id=28)
    tsettings = TournamentSettings.objects.get(tournament=tourn)
    if not tsettings.game_report_template:
        return ''

    gr_template = tsettings.game_report_template

    for file in files:
        wb = load_workbook(filename = os.path.join(settings.GAME_REPORT_DIR, 'post', file))
        ws = wb.active

        game_number = int(ws['T4'].value[1:])
        #game = Game.objects.filter(tournament=tourn, id_counter=game_number)
        games = Game.objects.select_related("tournament", "tournament_event__category", "team_st_a__team", "team_st_b__team").prefetch_related(
            Prefetch("team_a__player_set", queryset=Player.objects.all(), to_attr="players"),
            Prefetch("team_b__player_set", queryset=Player.objects.all(), to_attr="players"),
            Prefetch("playerstats_set", queryset=PlayerStats.objects.select_related("tournament_event__category", "player__team", "teamstat").all(), to_attr="pstat")
        ).filter(tournament=tourn)
        all_games = [g for g in games.all()]
        game = next(g for g in all_games if g.id_counter==game_number)
        players_a = game.team_a.players #[pl for pl in game.team_a.player_set.all()]
        players_b = game.team_b.players #[pl for pl in game.team_b.player_set.all()]
        all_pstats = game.pstat
        pstats_a = [ps for ps in all_pstats if ps.player.team.id == game.team_st_a.team.id]
        pstats_b = [ps for ps in all_pstats if ps.player.team.id == game.team_st_b.team.id]
        for ps in pstats_a:
            ps.spin_try = 0
            ps.spin_success = 0
            ps.one_try = 0
            ps.one_success = 0
            ps.shooter_success = 0
            ps.shooter_try = 0
            ps.kempa_try = 0
            ps.kempa_success = 0
            ps.score = 0
        for ps in pstats_b:
            ps.spin_try = 0
            ps.spin_success = 0
            ps.one_try = 0
            ps.one_success = 0
            ps.shooter_success = 0
            ps.shooter_try = 0
            ps.kempa_try = 0
            ps.kempa_success = 0
            ps.score = 0

        global_ps_a = PlayerStats.objects.filter(tournament_event=game.tournament_event, player__team=game.team_a, is_ranked=True).all()
        global_ps_b = PlayerStats.objects.filter(tournament_event=game.tournament_event, player__team=game.team_b, is_ranked=True).all()


        score_a_1 = ws['M40'].value
        score_a_2 = ws['T40'].value
        score_a_p = ws['T44'].value
        if score_a_p is None:
            score_a_p = 0
        score_a_1_act = 0
        score_a_2_act = 0
        score_a_p_act = 0

        score_b_1 = ws['O40'].value
        score_b_2 = ws['V40'].value
        score_b_p = ws['V44'].value
        if score_b_p is None:
            score_b_p = 0
        score_b_1_act = 0
        score_b_2_act = 0
        score_b_p_act = 0
        error_found = False
        # set 1 team a
        set1_start_row = 13
        set1_end_row = 32

        act_points = 0
        for iRow in range(1,21):
            act_points += 1
            act_row = set1_start_row + iRow
            print(str(ws['J' + str(act_row)].value))
            print(str(ws['B13'].value))
            if not ws['J' + str(act_row)].value is None:
                #player of a scored
                number = int(ws['J' + str(act_row)].value)
                player = next(pl for pl in players_a if pl.number == number)
                if player:
                    pstat = next(ps for ps in pstats_a if ps.player_id == player.id)
                    pstat_gl = next(ps for ps in global_ps_a if ps.player_id == player.id)
                    if pstat:
                        if act_points == 1:
                            pstat.one_success += 1
                            pstat.one_try += 1
                            pstat_gl.one_success += 1
                            pstat_gl.one_try += 1
                        else:
                            pstat.spin_success += 1
                            pstat.spin_try += 1
                            pstat_gl.spin_success += 1
                            pstat_gl.spin_try += 1
                        pstat.score += act_points
                        pstat_gl.score += act_points
                        score_a_1_act += act_points
                        if act_points == 1:
                            act_points = 0
                    else:
                        print('No PlayerStat found')
                else:
                    error_found = True
                    print('Playernumber not found '+ str(number))
            if act_points == 2:
                act_points = 0
        act_points = 0
        for iRow in range(1,21):
            act_points += 1
            act_row = set1_start_row + iRow
            if not ws['L' + str(act_row)].value is None:
                #player of a scored
                number = int(ws['L' + str(act_row)].value)
                player = next(pl for pl in players_b if pl.number == number)
                if player:
                    pstat = next(ps for ps in pstats_b if ps.player_id == player.id)
                    pstat_gl = next(ps for ps in global_ps_b if ps.player_id == player.id)
                    if pstat:
                        if act_points == 1:
                            pstat.one_success += 1
                            pstat.one_try += 1
                            pstat_gl.one_success += 1
                            pstat_gl.one_try += 1
                        else:
                            pstat.spin_success += 1
                            pstat.spin_try += 1
                            pstat_gl.spin_success += 1
                            pstat_gl.spin_try += 1
                        pstat.score += act_points
                        pstat_gl.score += act_points
                        score_b_1_act += act_points
                        if act_points == 1:
                            act_points = 0
                    else:
                        print('No PlayerStat found')
                else:
                    error_found = True
                    print('Playernumber not found '+ str(number))
            if act_points == 2:
                act_points = 0

        act_points = 0
        for iRow in range(1,21):
            act_points += 1
            act_row = set1_start_row + iRow
            print(str(ws['M' + str(act_row)].value))
            print(str(ws['B13'].value))
            if not ws['M' + str(act_row)].value is None:
                #player of a scored
                number = int(ws['M' + str(act_row)].value)
                player = next(pl for pl in players_a if pl.number == number)
                if player:
                    pstat = next(ps for ps in pstats_a if ps.player_id == player.id)
                    pstat_gl = next(ps for ps in global_ps_a if ps.player_id == player.id)
                    if pstat:
                        if act_points == 1:
                            pstat.one_success += 1
                            pstat.one_try += 1
                            pstat_gl.one_success += 1
                            pstat_gl.one_try += 1
                        else:
                            pstat.spin_success += 1
                            pstat.spin_try += 1
                            pstat_gl.spin_success += 1
                            pstat_gl.spin_try += 1
                        pstat.score += act_points
                        pstat_gl.score += act_points
                        score_a_1_act += act_points
                        if act_points == 1:
                            act_points = 0
                    else:
                        print('No PlayerStat found')
                else:
                    error_found = True
                    print('Playernumber not found '+ str(number))
            if act_points == 2:
                act_points = 0
        act_points = 0
        for iRow in range(1,21):
            act_points += 1
            act_row = set1_start_row + iRow
            if not ws['O' + str(act_row)].value is None:
                #player of a scored
                number = int(ws['O' + str(act_row)].value)
                player = next(pl for pl in players_b if pl.number == number)
                if player:
                    pstat = next(ps for ps in pstats_b if ps.player_id == player.id)
                    pstat_gl = next(ps for ps in global_ps_b if ps.player_id == player.id)
                    if pstat:
                        if act_points == 1:
                            pstat.one_success += 1
                            pstat.one_try += 1
                            pstat_gl.one_success += 1
                            pstat_gl.one_try += 1
                        else:
                            pstat.spin_success += 1
                            pstat.spin_try += 1
                            pstat_gl.spin_success += 1
                            pstat_gl.spin_try += 1
                        pstat.score += act_points
                        pstat_gl.score += act_points
                        score_b_1_act += act_points
                        if act_points == 1:
                            act_points = 0
                    else:
                        print('No PlayerStat found')
                else:
                    error_found = True
                    print('Playernumber not found '+ str(number))
            if act_points == 2:
                act_points = 0

        if score_a_1_act != score_a_1:
            print('ERROR Halftime 1')
            error_found = True
        if score_b_1_act != score_b_1:
            print('ERROR Halftime 1')
            error_found = True
        
        act_points = 0
        for iRow in range(1,21):
            act_points += 1
            act_row = set1_start_row + iRow
            print(str(ws['Q' + str(act_row)].value))
            print(str(ws['B13'].value))
            if not ws['Q' + str(act_row)].value is None:
                #player of a scored
                number = int(ws['Q' + str(act_row)].value)
                print(number)
                player = next((pl for pl in players_a if pl.number == number), None)
                if player:
                    pstat = next((ps for ps in pstats_a if ps.player_id == player.id), None)
                    pstat_gl = next((ps for ps in global_ps_a if ps.player_id == player.id), None)
                    if pstat and pstat_gl:
                        if act_points == 1:
                            pstat.one_success += 1
                            pstat.one_try += 1
                            pstat_gl.one_success += 1
                            pstat_gl.one_try += 1
                        else:
                            pstat.spin_success += 1
                            pstat.spin_try += 1
                            pstat_gl.spin_success += 1
                            pstat_gl.spin_try += 1
                        pstat.score += act_points
                        pstat_gl.score += act_points
                        score_a_2_act += act_points
                        if act_points == 1:
                            act_points = 0
                    else:
                        print('No PlayerStat found')
                        error_found = True
                else:
                    error_found = True
                    print('Playernumber not found '+ str(number))          
            if act_points == 2:
                act_points = 0
        act_points = 0
        for iRow in range(1,21):
            act_points += 1
            act_row = set1_start_row + iRow
            if not ws['S' + str(act_row)].value is None:
                #player of a scored
                number = int(ws['S' + str(act_row)].value)
                player = next(pl for pl in players_b if pl.number == number)
                if player:
                    pstat = next(ps for ps in pstats_b if ps.player_id == player.id)
                    pstat_gl = next(ps for ps in global_ps_b if ps.player_id == player.id)
                    if pstat:
                        if act_points == 1:
                            pstat.one_success += 1
                            pstat.one_try += 1
                            pstat_gl.one_success += 1
                            pstat_gl.one_try += 1
                        else:
                            pstat.spin_success += 1
                            pstat.spin_try += 1
                            pstat_gl.spin_success += 1
                            pstat_gl.spin_try += 1
                        pstat.score += act_points
                        pstat_gl.score += act_points
                        score_b_2_act += act_points
                        if act_points == 1:
                            act_points = 0
                    else:
                        print('No PlayerStat found')
            if act_points == 2:
                act_points = 0
        act_points = 0
        for iRow in range(1,21):
            act_points += 1
            act_row = set1_start_row + iRow
            print(str(ws['M' + str(act_row)].value))
            print(str(ws['B13'].value))
            if not ws['T' + str(act_row)].value is None:
                #player of a scored
                number = int(ws['T' + str(act_row)].value)
                player = next(pl for pl in players_a if pl.number == number)
                if player:
                    pstat = next(ps for ps in pstats_a if ps.player_id == player.id)
                    pstat_gl = next(ps for ps in global_ps_a if ps.player_id == player.id)
                    if pstat:
                        if act_points == 1:
                            pstat.one_success += 1
                            pstat.one_try += 1
                            pstat_gl.one_success += 1
                            pstat_gl.one_try += 1
                        else:
                            pstat.spin_success += 1
                            pstat.spin_try += 1
                            pstat_gl.spin_success += 1
                            pstat_gl.spin_try += 1
                        pstat.score += act_points
                        pstat_gl.score += act_points
                        score_a_2_act += act_points
                        if act_points == 1:
                            act_points = 0
                    else:
                        print('No PlayerStat found')
                else:
                    error_found = True
                    print('Playernumber not found '+ str(number))
            if act_points == 2:
                act_points = 0
        act_points = 0
        for iRow in range(1,21):
            act_points += 1
            act_row = set1_start_row + iRow
            if not ws['V' + str(act_row)].value is None:
                #player of a scored
                number = int(ws['V' + str(act_row)].value)
                player = next(pl for pl in players_b if pl.number == number)
                if player:
                    pstat = next(ps for ps in pstats_b if ps.player_id == player.id)
                    pstat_gl = next(ps for ps in global_ps_b if ps.player_id == player.id)
                    if pstat:
                        if act_points == 1:
                            pstat.one_success += 1
                            pstat.one_try += 1
                            pstat_gl.one_success += 1
                            pstat_gl.one_try += 1
                        else:
                            pstat.spin_success += 1
                            pstat.spin_try += 1
                            pstat_gl.spin_success += 1
                            pstat_gl.spin_try += 1
                        pstat.score += act_points
                        pstat_gl.score += act_points
                        score_b_2_act += act_points
                        if act_points == 1:
                            act_points = 0
                    else:
                        print('No PlayerStat found')
                else:
                    error_found = True
                    print('Playernumber not found '+ str(number))
            if act_points == 2:
                act_points = 0
        
        if score_a_2_act != score_a_2:
            print('ERROR Halftime 2')
            error_found = True
        if score_b_2_act != score_b_2:
            print('ERROR Halftime 2')
            error_found = True
              
        # penalty
        act_points = 0
        for iRow in range(11,16):
            print(str(ws.cell(column=iRow, row=48).value))
            if not ws.cell(column=iRow, row=48).value is None and not ws.cell(column=iRow, row=50).value is None:
                #player of a scored
                number = int(ws.cell(column=iRow, row=48).value)
                print(number)
                score = int(ws.cell(column=iRow, row=50).value)
                if not score is None:
                    player = next(pl for pl in players_a if pl.number == number)
                    if player:
                        pstat = next((ps for ps in pstats_a if ps.player_id == player.id), None)
                        pstat_gl = next((ps for ps in global_ps_a if ps.player_id == player.id), None)
                        if pstat and pstat_gl:
                            if score == 1:
                                pstat.one_success += 1
                                pstat.one_try += 1
                                pstat_gl.one_success += 1
                                pstat_gl.one_try += 1
                            else:
                                pstat.spin_success += 1
                                pstat.spin_try += 1
                                pstat_gl.spin_success += 1
                                pstat_gl.spin_try += 1
                            pstat.score += score
                            pstat_gl.score += score
                            score_a_p_act += score
                        else:
                            print('No PlayerStat found')
                            error_found = True
                    else:
                        error_found = True
                        print('Playernumber not found '+ str(number))
            if not ws.cell(column=iRow, row=52).value is None and not ws.cell(column=iRow, row=54).value is None:
                #player of a scored
                number = int(ws.cell(column=iRow, row=52).value)
                score = int(ws.cell(column=iRow, row=54).value)
                if not score is None:
                    player = next(pl for pl in players_b if pl.number == number)
                    if player:
                        pstat = next((ps for ps in pstats_b if ps.player_id == player.id), None)
                        pstat_gl = next((ps for ps in global_ps_b if ps.player_id == player.id), None)
                        if pstat and pstat_gl:
                            if act_points == 1:
                                pstat.one_success += 1
                                pstat.one_try += 1
                                pstat_gl.one_success += 1
                                pstat_gl.one_try += 1
                            else:
                                pstat.spin_success += 1
                                pstat.spin_try += 1
                                pstat_gl.spin_success += 1
                                pstat_gl.spin_try += 1
                            pstat.score += score
                            pstat_gl.score += score
                            score_b_p_act += score
                        else:
                            print('No PlayerStat found')
                            error_found = True
                    else:
                        error_found = True
                        print('Playernumber not found '+ str(number))
        if score_a_p_act != score_a_p:
            print('ERROR Penalty')
            error_found = True
        if score_b_p_act != score_b_p:
            print('ERROR Penalty')
            error_found = True

        for psg in global_ps_a:
            psg.games_played += 1
        for psg in global_ps_b:
            psg.games_played += 1
        if not error_found:
            # save
            #['score','kempa_try', 'kempa_success','kempa_try', 'spin_success','spin_try', 'shooter_success','shooter_try', 'one_try', 'one_success']
            PlayerStats.objects.bulk_update(pstats_a, fields=['score','spin_success','spin_try', 'one_try', 'one_success'])
            PlayerStats.objects.bulk_update(pstats_b, fields=['score','spin_success','spin_try', 'one_try', 'one_success', 'games_played'])
            PlayerStats.objects.bulk_update(global_ps_a, fields=['score','spin_success','spin_try', 'one_try', 'one_success'])
            PlayerStats.objects.bulk_update(global_ps_b, fields=['score','spin_success','spin_try', 'one_try', 'one_success'])

        tstage = game.tournament_state.tournament_stage
        
        ws["T4"] = game.tournament_event.category.abbreviation + str(game.id_counter)
        