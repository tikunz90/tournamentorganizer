from django.shortcuts import get_object_or_404
from django import forms
from django.forms import ModelForm
from ...models.Tournament import Court, TournamentSettings

from bootstrap_modal_forms.forms import BSModalModelForm

class TournamentSettingsForm(ModelForm):
    class Meta:
        model = TournamentSettings
        fields = '__all__'
        exclude = ('tournament',)

class CourtForm(BSModalModelForm):

    def clean(self):
        cleaned_data = super(CourtForm, self).clean()
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
