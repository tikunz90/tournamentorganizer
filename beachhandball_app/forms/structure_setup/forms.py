from beachhandball_app.models.Game import Game
from beachhandball_app.models.Team import TeamStats
from django import forms
from django.forms import ModelForm
from ...models.Tournament import TournamentState, TournamentStage, TournamentTeamTransition

from colorfield.widgets import ColorWidget
from bootstrap_modal_forms.forms import BSModalModelForm

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


class TournamentStateForm(BSModalModelForm):

    def clean(self):
        print('Clean TournamentStateForm')
        cleaned_data = super(TournamentStateForm, self).clean()
        name = self.cleaned_data['name']
        tstage = self.cleaned_data['tournament_stage']
        
        #if TournamentState.objects.filter(name = name, tournament_stage=tstage).exists():
        #    self.add_error('name', 'Already exists!')
        

        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return cleaned_data
    
    
    class Meta:
        model = TournamentState
        exclude = ['tournament_event', 'tournament_state','grid_row', 'grid_col']
        widgets = {
           'color': forms.widgets.TextInput(attrs={'type': 'color'}),
        }

class TournamentStateUpdateForm(BSModalModelForm):

    def clean(self):
        print('Clean TournamentStateForm')
        cleaned_data = super(TournamentStateUpdateForm, self).clean()
        return cleaned_data
    class Meta:
        model = TournamentState
        fields = ('name', 'max_number_teams', 'color')
        widgets = {
           'color': forms.widgets.TextInput(attrs={'type': 'color'}),
        }


class TeamStatsUpdateTeamForm(BSModalModelForm):

    def clean(self):
        print('Clean TeamStatsUpdateTeamForm')
        cleaned_data = super(TeamStatsUpdateTeamForm, self).clean()
        return cleaned_data
    class Meta:
        model = TeamStats
        fields = ['team', 'rank_initial']


class TTTUpdateForm(BSModalModelForm):

    def clean(self):
        print('Clean TTTUpdateForm')
        cleaned_data = super(TTTUpdateForm, self).clean()
        return cleaned_data
    class Meta:
        model = TournamentTeamTransition
        fields = ['target_ts_id', 'target_rank']


class GameUpdateForm(BSModalModelForm):

    def clean(self):
        cleaned_data = super(GameUpdateForm, self).clean()
        return cleaned_data
    class Meta:
        model = Game
        fields = '__all__'