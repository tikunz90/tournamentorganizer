from beachhandball_app.models.choices import CATEGORY_CHOICES
import os
from shutil import copyfile

from openpyxl import load_workbook

from django.conf import settings

def create_pregame_report_excel(game):
    print('ENTER create_report_excel')
    print('game_report DIR: ' + settings.GAME_REPORT_DIR)

    filename_template = 'game_report_template.xlsx'
    filename = 'PreGame_' + game.tournament_event.category.abbreviation + str(game.id) + '.xlsx'

    fullfilepath_template = os.path.join(settings.GAME_REPORT_DIR, filename_template)
    fullfilepath_report = os.path.join(settings.GAME_REPORT_DIR, filename)
    # copy template
    copyfile(fullfilepath_template, fullfilepath_report)

    if os.path.isfile(fullfilepath_report):
        print('file exists')
        wb = load_workbook(filename = fullfilepath_report)
        ws = wb.active

        # game id
        ws["T4"] = game.tournament_event.category.abbreviation + str(game.id)
        
        # category
        if game.tournament_event.category.category == CATEGORY_CHOICES[0][0]:
            ws["M3"] = 'X'
        elif game.tournament_event.category.category == CATEGORY_CHOICES[1][0]:
            ws["P3"] = 'X'

        # court
        ws["R8"] = game.court.number

        # team names
        ws["B8"] = game.team_st_a.team.name
        ws["G8"] = game.team_st_b.team.name

        # Date and Time
        date = game.starttime.strftime("%d.%m.%Y")
        time = game.starttime.strftime("%H:%M")
        ws["C10"] = date
        ws["F10"] = time
        max_num_player = 10
        row_start_a = 13
        for player in game.team_st_a.team.player_set.all()[:max_num_player]:
            ws["A"+str(row_start_a)]=player.number
            ws["B"+str(row_start_a)]=player.name + ", " + player.first_name
            row_start_a = row_start_a + 1
        row_start_b = 30
        for player in game.team_st_b.team.player_set.all()[:max_num_player]:
            ws["A"+str(row_start_b)]=player.number
            ws["B"+str(row_start_b)]=player.name + ", " + player.first_name
            row_start_b = row_start_b + 1
        wb.save(fullfilepath_report)

        return fullfilepath_report, filename
    return ''