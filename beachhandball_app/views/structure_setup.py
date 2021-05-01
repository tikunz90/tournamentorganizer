from datetime import datetime
from beachhandball_app.models.Game import Game
from beachhandball_app.models.Game import Game
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.messages.views import SuccessMessageMixin

from beachhandball_app.helper import reverse_querystring

from bootstrap_modal_forms.generic import BSModalCreateView, BSModalDeleteView, BSModalUpdateView

from ..models.Tournament import Tournament, TournamentEvent, TournamentStage, TournamentState, TournamentTeamTransition
from ..models.Series import Season
from ..models.Team import Team, TeamStats

from beachhandball_app.forms.structure_setup.forms import GameUpdateForm, TTTUpdateForm, TournamentStageForm, TournamentStateForm, TournamentStateUpdateForm, TeamStatsUpdateTeamForm

from beachhandball_app import static_views

#class StructureSetupDetail(LoginRequiredMixin, DetailView):
class StructureSetupDetail(DetailView):
    model = TournamentEvent
    template_name = 'beachhandball/tournamentevent/structure_setup.html'
    login_url = '/login/'
    redirect_field_name = 'structure_setup'

    def get_context_data(self, **kwargs):
        print('Enter StructureSetupDetail: ', datetime.now())
        tevent = kwargs["object"]
        t = Tournament.objects.get(id=1)
        #tevent = TournamentEvent.objects.filter(tournament=t).prefetch_related('TournamentStages')
        context = {}
        kwargs['tourn'] = t
        kwargs['tst_view'] = tevent.tournamentstage_set.all()

        kwargs['tevent'] = tevent 
        #kwargs = static_views.getContext(self.request)
        kwargs['tournaments_active'] = 'active_detail'
        kwargs['segment'] = 'structure_setup'
        kwargs['segment_title'] = 'Structure Setup \ ' + tevent.name_short

        kwargs['ts_types'] = TournamentStage.objects.filter(tournament_event=tevent)
        kwargs['teams_appending'] = []#Team.objects.filter(tournament=tevent)
        
        #tstate = TournamentState.objects.get(id=6)
       # kwargs['form_tstate'] = TournamentStateUpdateForm(instance=tstate)
        print('Leave StructureSetupDetail: ', datetime.now())
        return super(StructureSetupDetail, self).get_context_data(**kwargs)


class StageCreateView(BSModalCreateView):
    template_name = 'beachhandball/tournamentevent/create_stage_form.html'
    form_class = TournamentStageForm
    success_message = 'Success: Stage was created.'

    def get_initial(self):
        tevent = get_object_or_404(TournamentEvent, id=self.kwargs.get('pk'))
        return {
            'tournament_event':tevent,
        }

    def get_success_url(self):
           pk = self.kwargs["pk"]
           return reverse("structure_setup.detail", kwargs={"pk": pk})

class StageDeleteView(BSModalDeleteView):
    model = TournamentStage
    template_name = 'beachhandball/tournamentevent/delete_stage.html'
    success_message = 'Success: Stage was deleted.'

    def get_success_url(self):
           pk = self.kwargs["pk_tevent"]
           return reverse("structure_setup.detail", kwargs={"pk": pk})


class StateCreateView(BSModalCreateView):
    template_name = 'beachhandball/templates/create_form.html'
    form_class = TournamentStateForm
    success_message = 'Success: State was created.'

    def get_initial(self):
        tevent = get_object_or_404(TournamentEvent, id=self.kwargs.get('pk_tevent'))
        tstage = get_object_or_404(TournamentStage, id=self.kwargs.get('pk_tstage'))
        return {
            'tournament_event':tevent,
            'tournament_stage':tstage,
        }
    
    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        tevent = get_object_or_404(TournamentEvent, id=self.kwargs.get('pk_tevent'))
        tstage = get_object_or_404(TournamentStage, id=self.kwargs.get('pk_tstage'))
        form.instance.tournament_event = tevent
        form.instance.tournament_stage = tstage
        return super().form_valid(form)

    def get_success_url(self):
           pk = self.kwargs["pk_tevent"]
           return reverse("structure_setup.detail", kwargs={"pk": pk})


class StateDeleteView(BSModalDeleteView):
    model = TournamentState
    template_name = 'beachhandball/tournamentevent/delete_state.html'
    success_message = 'Success: Stage was deleted.'

    def get_success_url(self):
           pk = self.kwargs["pk_tevent"]
           return reverse("structure_setup.detail", kwargs={"pk": pk})


class StateUpdateView(BSModalUpdateView):
    model = TournamentState
    template_name = 'beachhandball/templates/update_form.html'
    form_class = TournamentStateUpdateForm
    success_message = 'Success: State was updated.'
    
    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        tevent = get_object_or_404(TournamentEvent, id=self.kwargs.get('pk_tevent'))
        tstage = get_object_or_404(TournamentStage, id=self.kwargs.get('pk_tstage'))
        form.instance.tournament_event = tevent
        form.instance.tournament_stage = tstage
        return super().form_valid(form)

    def get_success_url(self):
           pk = self.kwargs["pk_tevent"]
           return reverse_querystring("structure_setup.detail", kwargs={"pk": pk}, query_kwargs={'tab': self.kwargs["pk_tstage"]})

class TeamStatsUpdateTeamView(BSModalUpdateView):
    model = TeamStats
    template_name = 'beachhandball/templates/update_teamstat_form.html'
    form_class = TeamStatsUpdateTeamForm
    success_message = 'Success: TeamStat was updated.'
    
    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        tevent = get_object_or_404(TournamentEvent, id=self.kwargs.get('pk_tevent'))
        tstage = get_object_or_404(TournamentStage, id=self.kwargs.get('pk_tstage'))
        form.instance.tournament_event = tevent
        form.instance.tournament_stage = tstage
        return super().form_valid(form)

    def get_success_url(self):
           pk = self.kwargs["pk_tevent"]
           return reverse_querystring("structure_setup.detail", kwargs={"pk": pk}, query_kwargs={'tab': self.kwargs["pk_tstage"], 'tab_tstate': 1})


class TTTUpdateView(BSModalUpdateView):
    model = TournamentTeamTransition
    template_name = 'beachhandball/templates/update_form.html'
    form_class = TTTUpdateForm
    success_message = 'Success: TeamStat was updated.'
    
    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        tevent = get_object_or_404(TournamentEvent, id=self.kwargs.get('pk_tevent'))
        tstage = get_object_or_404(TournamentStage, id=self.kwargs.get('pk_tstage'))
        form.instance.tournament_event = tevent
        form.instance.tournament_stage = tstage
        return super().form_valid(form)

    def get_success_url(self):
           pk = self.kwargs["pk_tevent"]
           return reverse_querystring("structure_setup.detail", kwargs={"pk": pk}, query_kwargs={'tab': self.kwargs["pk_tstage"], 'tab_tstate': 2})


class GameUpGameView(BSModalUpdateView):
    model = Game
    template_name = 'beachhandball/templates/update_form.html'
    form_class = GameUpdateForm
    success_message = 'Success: Game was updated.'
    
    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        tevent = get_object_or_404(TournamentEvent, id=self.kwargs.get('pk_tevent'))
        tstage = get_object_or_404(TournamentStage, id=self.kwargs.get('pk_tstage'))
        form.instance.tournament_event = tevent
        form.instance.tournament_stage = tstage
        return super().form_valid(form)

    def get_success_url(self):
           pk = self.kwargs["pk_tevent"]
           return reverse_querystring("structure_setup.detail", kwargs={"pk": pk}, query_kwargs={'tab': self.kwargs["pk_tstage"], 'tab_tstate': 0})
