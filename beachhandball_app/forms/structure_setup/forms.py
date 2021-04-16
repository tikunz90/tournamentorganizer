from django import forms
from django.forms import ModelForm
from ...models.Tournament import TournamentStage


class TournamentStageForm(ModelForm):

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
