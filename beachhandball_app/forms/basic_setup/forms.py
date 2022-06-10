from django.shortcuts import get_object_or_404
from django import forms
from django.forms import ModelForm

from beachhandball_app.models.General import GameReportTemplate
from ...models.Tournaments import Court, TournamentSettings

from bootstrap_modal_forms.forms import BSModalModelForm

class TournamentSettingsForm(ModelForm):
    class Meta:
        model = TournamentSettings
        fields = ('game_report_template', 'first_game_slot', 'game_slot_mins', 'game_slot_counter', 'amount_players_report', 'amount_officials_report')
        exclude = ('tournament',)

        widgets = {
           'first_game_slot': forms.widgets.DateTimeInput(attrs={'class': "form-control datetimepicker"}),
           #'actual_game_slot': forms.widgets.DateTimeInput(attrs={'class': "form-control datetimepicker"}),
        }

    def __init__(self, *args, **kwargs):
        super(TournamentSettingsForm, self).__init__(*args, **kwargs)
        self.fields['game_report_template'].queryset = GameReportTemplate.objects.all()

class CourtForm(ModelForm):

    def clean(self):
        cleaned_data = super(CourtForm, self).clean()
        tournament = cleaned_data['tournament']
        name = cleaned_data['name']
        number = cleaned_data['number']
        
        if Court.objects.filter(tournament = tournament, name = name, number=number).exists():
            self.add_error('name', 'Already exists!')
        return cleaned_data
       
    class Meta:
        model = Court
        fields = '__all__'
        widgets = {
            'tournament': forms.widgets.Select(attrs={'class': "form-control selectpicker", 'data-style':"btn btn-info btn-round"}),
        }

class CourtUpdateForm(BSModalModelForm):

    class Meta:
        model = Court
        fields = '__all__'
        widgets = {
            'tournament': forms.widgets.Select(attrs={'class': "form-control selectpicker", 'data-style':"btn btn-info btn-round"}),
        }
