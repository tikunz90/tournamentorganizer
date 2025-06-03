import json
from django.db.models import fields
from django.shortcuts import get_object_or_404
from beachhandball_app.game_report import helper_game_report
from beachhandball_app.helper import calculate_tstate
from beachhandball_app.models.Game import Game
from beachhandball_app.models.Team import Team, TeamStats
from django import forms
from django.forms import ModelForm, widgets

from beachhandball_app.models.choices import GAMESTATE_CHOICES
from ...models.Tournaments import TournamentEvent, TournamentState, TournamentStage, TournamentTeamTransition

from colorfield.widgets import ColorWidget
from bootstrap_modal_forms.forms import BSModalModelForm
from bootstrap_modal_forms.utils import is_ajax

from ...models.choices import ROUND_TYPES, TOURNAMENT_STAGE_TYPE_CHOICES, TOURNAMENT_STATE_CHOICES

"""

Tournament Stage Forms

"""
class TournamentStageForm(BSModalModelForm):

    def clean(self):
        print('Clean TournamentStageForm')
        cleaned_data = super(TournamentStageForm, self).clean()
        name = self.cleaned_data['name']
        tevent = self.cleaned_data['tournament_event']
        
        if TournamentStage.objects.filter(name = name, tournament_event=tevent).exists():
            self.add_error('name', 'Already exists!')
        

        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return cleaned_data

    class Meta:
        model = TournamentStage
        exclude = []
        widgets = {
            'tournament_event': forms.widgets.Select(attrs={'class': "form-control selectpicker", 'data-style':"btn btn-info btn-round"}),
            'tournament_stage': forms.widgets.Select(attrs={'class': "form-control selectpicker", 'data-style':"btn btn-info btn-round"}),
        }

        #def __init__(self, *args, **kwargs):
        #    super(TournamentStageForm, self).__init__(*args, **kwargs)
        #    self.fields['id_tournament_event'].disabled = True
        #    self.initial['id_tournament_event'] = self.kwargs['pk']
        #    for visible in self.visible_fields():
        #        if ( visible.field.widget.type == 'select'):
        #            visible.field.widget.attrs['class'] = 'selectpicker'
        #            visible.field.widget.attrs['data-style'] = 'btn btn-default'
        #        else:
        #            visible.field.widget.attrs['class'] = 'form-control'


"""

Tournament State Forms

"""

class TournamentStateForm(BSModalModelForm):

    round_type = forms.ChoiceField(choices=[(round_type.value, round_type.value) for round_type in ROUND_TYPES], label='Round Types', widget=forms.Select(attrs={'class': "form-control selectpicker", 'data-style':"btn btn-info btn-round"}))

    def clean(self):
        print('Clean TournamentStateForm')
        cleaned_data = super(TournamentStateForm, self).clean()
        name = self.cleaned_data['name']
        tstage = self.cleaned_data['tournament_stage']

        if tstage.tournament_stage == TOURNAMENT_STAGE_TYPE_CHOICES[3][1]:
            states = TournamentState.objects.filter(tournament_stage=tstage).all()
            hierarchy = 500
            for s in states:
                if s.hierarchy > hierarchy:
                    hierarchy = s.hierarchy
            hierarchy += 1
            self.cleaned_data['hierarchy'] = hierarchy
            self.cleaned_data['tournament_state'] = TOURNAMENT_STATE_CHOICES[-6][1]
        # if TournamentState.objects.filter(name=name, tournament_stage=tstage).exists():
        #    self.add_error('name', 'Already exists!')

        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return cleaned_data

    class Meta:
        model = TournamentState
        exclude = ['tournament_event', 'tournament_state', 'grid_row', 'grid_col', 'is_populated', 'is_final', 'is_finished', 'transitions_done', 'min_number_teams']
        widgets = {
            'tournament_stage': forms.widgets.Select(attrs={'class': "form-control selectpicker", 'data-style': "btn btn-info btn-round"}),
            'color': forms.widgets.TextInput(attrs={'type': 'color'}),
        }

class TournamentStateUpdateForm(BSModalModelForm):

    def __init__(self, *args, **kwargs):
        super(TournamentStateUpdateForm, self).__init__(*args, **kwargs)
        self.fields['order'].label = "display order GBO App"

    def clean(self):
        print('Clean TournamentStateForm')
        cleaned_data = super(TournamentStateUpdateForm, self).clean()
        return cleaned_data
    class Meta:
        model = TournamentState
        fields = ('name', 'abbreviation', 'max_number_teams', 'direct_compare', 'color', 'order')
        widgets = {
           'color': forms.widgets.TextInput(attrs={'type': 'color'}),
        }

class TournamentStateFinishForm(BSModalModelForm):
    disabled_fields = ('name',)
    def clean(self):
        print('Clean TournamentStateForm')
        cleaned_data = super(TournamentStateFinishForm, self).clean()
        return cleaned_data
    class Meta:
        model = TournamentState
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        super(TournamentStateFinishForm, self).__init__(*args, **kwargs)
        for field in self.disabled_fields:
            self.fields[field].disabled = True



"""

Team Stats Forms

"""

class TeamStatsUpdateTeamForm(BSModalModelForm):

    def clean(self):
        print('Clean TeamStatsUpdateTeamForm')
        cleaned_data = super(TeamStatsUpdateTeamForm, self).clean()
        return cleaned_data
    class Meta:
        model = TeamStats
        fields = ['team']
        widgets = {
            'team': forms.widgets.Select(attrs={'class': "form-control selectpicker", 'data-style':"btn btn-info btn-round"}),
        }

    def __init__(self, *args, **kwargs):
        super(TeamStatsUpdateTeamForm, self).__init__(*args, **kwargs)
        self.fields['team'].queryset = Team.objects.filter(is_dummy=False)

class TeamStatsUpdateInitialTeamForm(forms.ModelForm):
    disabled_fields = ('rank_initial',)
    class Meta:
        model = TeamStats
        fields = ['id', 'rank_initial', 'team']
        widgets = {
            'team': forms.widgets.Select(attrs={
                'class': "form-control selectpicker",
                'data-style': "btn btn-info btn-round",
                'data-live-search': "true",
                'data-container': "body",
            }),
        }

    def __init__(self, *args, tevent=None, teams=None, **kwargs):
        super().__init__(*args, **kwargs)
        if teams is not None:
            self.fields['team'].queryset = teams
        elif tevent is not None:
            self.fields['team'].queryset = Team.objects.filter(tournament_event=tevent, is_dummy=False)
        else:
            raise ValueError("TeamStatsUpdateInitialTeamForm requires either 'tevent' or 'teams' argument.")
        for field in self.disabled_fields:
            if field in self.fields:
                self.fields[field].disabled = True

"""

Tournament Team Transisiton Forms

"""

class TTTUpdateForm(BSModalModelForm):

    def clean(self):
        print('Clean TTTUpdateForm')
        cleaned_data = super(TTTUpdateForm, self).clean()
        return cleaned_data
    class Meta:
        model = TournamentTeamTransition
        fields = ['target_ts_id', 'target_rank', 'keep_stats']
        widgets = {
            'target_ts_id': forms.widgets.Select(attrs={'class': "form-control selectpicker", 'data-style':"btn btn-info btn-round"}),
        }

"""

Game Forms

"""
class GameUpdateForm(BSModalModelForm):
    disabled_fields = ('tournament_state',)

    def clean(self):
        cleaned_data = super(GameUpdateForm, self).clean()
        return cleaned_data
    class Meta:
        model = Game
        fields = ('team_st_a', 'team_st_b', 'tournament_state', 'ref_a', 'ref_b', 'starttime', 'court', 'gamestate', 'gamingstate', 'scouting_state')
        labels = {
            'team_st_a': 'Team A:',
            'team_st_b': 'Team B:',
        }
        widgets = {
            'team_st_a': forms.widgets.Select(attrs={'class': "form-control selectpicker", 'data-style':"btn btn-info btn-round"}),
            'team_st_b': forms.widgets.Select(attrs={'class': "form-control selectpicker", 'data-style':"btn btn-info btn-round"}),
            'ref_a': forms.widgets.Select(attrs={'class': "form-control selectpicker", 'data-style':"btn btn-info btn-round"}),
            'ref_b': forms.widgets.Select(attrs={'class': "form-control selectpicker", 'data-style':"btn btn-info btn-round"}),
            'court': forms.widgets.Select(attrs={'class': "form-control selectpicker", 'data-style':"btn btn-info btn-round"}),
           'tournament_state': forms.widgets.Select(attrs={'class': "form-control selectpicker", 'data-style':"btn btn-info btn-round"}),
           'starttime': forms.widgets.DateTimeInput(attrs={'class': "form-control datetimepicker"}),
           'gamestate': forms.widgets.Select(attrs={'class': "form-control selectpicker", 'data-style':"btn btn-info btn-round"}),
           'gamingstate': forms.widgets.Select(attrs={'class': "form-control selectpicker", 'data-style':"btn btn-info btn-round"}),
           'scouting_state': forms.widgets.Select(attrs={'class': "form-control selectpicker", 'data-style':"btn btn-info btn-round"}),
        }

    def __init__(self, *args, **kwargs):
        super(GameUpdateForm, self).__init__(*args, **kwargs)
        for field in self.disabled_fields:
            self.fields[field].disabled = True
        #self.fields['starttime'].widget.attrs['class'] = 'form-control datetimepicker'
        
class GameUpdateResultForm(BSModalModelForm):

    def save(self, commit=True):
        game = super().save(commit=False)
        calculate_tstate(game.tournament_state)
    #    if commit and not is_ajax(self.request.META):
    #        game.gamestate = GAMESTATE_CHOICES[2][0]
    #        game.save()
    #        #calculate_tstate(self.object.tournament_state)
    #        if self.data['upload-data']:
    #            upload_data = json.loads(self.data['upload-data'])
    #            helper_game_report.import_playerstats_game_report(game, upload_data)
    #        
        return game

    def clean(self):
        cleaned_data = super(GameUpdateResultForm, self).clean()
        return cleaned_data
    class Meta:
        model = Game
        fields = ('score_team_a_halftime_1', 'score_team_a_halftime_2', 'score_team_a_penalty', 'score_team_b_halftime_1', 'score_team_b_halftime_2', 'score_team_b_penalty', 'gamestate')
        labels = {
            'score_team_a_halftime_1': 'Score',
        }
        widgets = {
            'gamestate': forms.widgets.Select(attrs={'class': "form-control selectpicker", 'data-style':"btn btn-info btn-round"}),
        }


class GameForm(BSModalModelForm):

    def clean(self):
        print('Clean Game')
        cleaned_data = super(GameForm, self).clean()
       
        #if TournamentState.objects.filter(name = name, tournament_stage=tstage).exists():
        #    self.add_error('name', 'Already exists!')
        

        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return cleaned_data
    
    
    class Meta:
        model = Game
        exclude = ['duration_of_halftime', 'number_of_penalty_tries', 'score_team_a_halftime_1', 'score_team_a_halftime_2', 'score_team_a_penalty', 'score_team_b_halftime_1', 'score_team_b_halftime_2', 'score_team_b_penalty', 'winner_halftime_1', 'winner_halftime_2', 'winner_penalty', 'act_time']
        widgets = {
            'tournament': forms.widgets.Select(attrs={'class': "form-control selectpicker", 'data-style':"btn btn-info btn-round"}),
            'tournament_event': forms.widgets.Select(attrs={'class': "form-control selectpicker", 'data-style':"btn btn-info btn-round"}),
            'tournament_state': forms.widgets.Select(attrs={'class': "form-control selectpicker", 'data-style':"btn btn-info btn-round"}),
            'team_st_a': forms.widgets.Select(attrs={'class': "form-control selectpicker", 'data-style':"btn btn-info btn-round"}),
            'team_st_b': forms.widgets.Select(attrs={'class': "form-control selectpicker", 'data-style':"btn btn-info btn-round"}),
            'ref_a': forms.widgets.Select(attrs={'class': "form-control selectpicker", 'data-style':"btn btn-info btn-round"}),
            'ref_b': forms.widgets.Select(attrs={'class': "form-control selectpicker", 'data-style':"btn btn-info btn-round"}),
            'gamestate': forms.widgets.Select(attrs={'class': "form-control selectpicker", 'data-style':"btn btn-info btn-round"}),
            'gamingstate': forms.widgets.Select(attrs={'class': "form-control selectpicker", 'data-style':"btn btn-info btn-round"}),
            'scouting_state': forms.widgets.Select(attrs={'class': "form-control selectpicker", 'data-style':"btn btn-info btn-round"}),
            'starttime': forms.widgets.DateTimeInput(attrs={'class': "form-control datetimepicker"}),
            'court': forms.widgets.Select(attrs={'class': "form-control selectpicker", 'data-style':"btn btn-info btn-round"}),
        }