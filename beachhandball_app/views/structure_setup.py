from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse

from ..models.Tournament import Tournament, TournamentEvent, TournamentStage
from ..models.Series import Season
from ..models.Team import Team

from beachhandball_app.forms.structure_setup.forms import TournamentStageForm

from beachhandball_app import static_views

#class StructureSetupDetail(LoginRequiredMixin, DetailView):
class StructureSetupDetail(DetailView):
    model = TournamentEvent
    template_name = 'beachhandball/tournamentevent/structure_setup.html'
    login_url = '/login/'
    redirect_field_name = 'structure_setup'

    def get_context_data(self, **kwargs):
        tevent = kwargs["object"]
        t = Tournament.objects.get(id=1)
        #tevent = TournamentEvent.objects.filter(tournament=t).prefetch_related('TournamentStages')
        context = {}
        
        kwargs['tst_view'] = tevent.tournamentstage_set.all()

        kwargs['tevent'] = tevent 
        #kwargs = static_views.getContext(self.request)
        kwargs['tournaments_active'] = 'active_detail'
        kwargs['segment'] = 'structure_setup'
        kwargs['segment_title'] = 'Structure Setup \ ' + tevent.name_short

        kwargs['ts_types'] = TournamentStage.objects.filter(tournament_event=tevent)
        kwargs['teams_appending'] = []#Team.objects.filter(tournament=tevent)

        return super(StructureSetupDetail, self).get_context_data(**kwargs)


class StructureSetupCreateTournamentStage(CreateView):
    model = TournamentStage
    form_class = TournamentStageForm
    #fields = '__all__'
    template_name = 'beachhandball/tournamentevent/structure_setup_create_stage.html'
    
    #def get_initial(self, *args, **kwargs):
    #    initial = super(StructureSetupCreateTournamentStage, self).get_initial(**kwargs)
    #    initial['tournament_event_id'] = 1
    #    return initial

    def get_context_data(self, **kwargs):
        t = Tournament.objects.get(id=1)
        tevent =TournamentEvent.objects.filter(tournament=t, id=self.kwargs['pk']).first()
        kwargs['tevent'] = tevent
        kwargs['form_title'] = 'Create Stage'
        kwargs['tournaments_active'] = 'active_detail'
        kwargs['segment'] = 'structure_setup'
        kwargs['segment_title'] = 'Structure Setup \ ' + tevent.name_short
        return super(StructureSetupCreateTournamentStage, self).get_context_data(**kwargs)

    #def form_valid(self, form):
    #    form.instance.tournament_event_id = 2
    #    return super(StructureSetupCreateTournamentStage, self).form_valid(form)

    def get_success_url(self):
           pk = self.kwargs["pk"]
           return reverse("structure_setup.detail", kwargs={"pk": pk})