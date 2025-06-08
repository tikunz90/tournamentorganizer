from datetime import datetime

from django.views.generic.base import RedirectView
from beachhandball_app import helper
from beachhandball_app.models.Game import Game
from beachhandball_app.models.Game import Game
from django.conf import settings
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
from beachhandball_app.helper import reverse_querystring, calculate_tstate

from bootstrap_modal_forms.generic import BSModalCreateView, BSModalDeleteView, BSModalUpdateView

from ..models.Tournaments import Tournament, TournamentEvent, TournamentStage, TournamentState, TournamentTeamTransition
from ..models.Series import Season
from ..models.Team import Team, TeamStats

from beachhandball_app.forms.structure_setup.forms import GameUpdateForm, GameUpdateResultForm, TTTUpdateForm, TournamentStageForm, TournamentStateForm, TournamentStateUpdateForm, TeamStatsUpdateTeamForm, GameForm

from beachhandball_app import helper

#class StructureSetupDetail(LoginRequiredMixin, DetailView):
class ResultsDetail(DetailView):
    model = TournamentEvent
    template_name = 'beachhandball/tournamentevent/results.html'
    login_url = '/login/'
    redirect_field_name = 'results'

    def dispatch(self, request, *args, **kwargs):
        context = helper.getContext(self.request)
        if not helper.checkLoginIsValid(context['gbo_user']):
            return RedirectView('login')
        self.kwargs['context_data'] = context
        
        return super(ResultsDetail, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        print('Enter ResultsDetail: ', datetime.now())
        tevent = kwargs["object"]
        
        #if settings.DEBUG is True:
        #    t = Tournament.objects.get(id=2)
        #else:
        context = self.kwargs['context_data']
        t = context['tourn']
        kwargs['events'] = context['events']
        #tevent = TournamentEvent.objects.filter(tournament=t).prefetch_related('TournamentStages')
        context = {}
        kwargs['tourn'] = t
        kwargs['tevent'] = tevent 
        #kwargs = static_views.getContext(self.request)
        kwargs['tournaments_active'] = 'active_detail'
        kwargs['segment'] = 'results'
        kwargs['segment_title'] = 'Results \ ' + tevent.name_short + ' ' + tevent.category.name + ' ' +tevent.category.classification
        kwargs['playerstats_offense'] = tevent.playerstats_set.filter(is_ranked=True).select_related('player__team').order_by('-score')[:50]
        kwargs['playerstats_defense'] = tevent.playerstats_set.filter(is_ranked=True).select_related('player__team').order_by('-block_success')[:50]
        kwargs['playerstats_goalie'] = tevent.playerstats_set.filter(is_ranked=True).select_related('player__team').order_by('-goal_keeper_success')[:50]
        
        #tstate = TournamentState.objects.get(id=6)
       # kwargs['form_tstate'] = TournamentStateUpdateForm(instance=tstate)

        #helper.set_seasoncupid_to_all_global_pstats(tevent, 5)

        print('Leave ResultsDetail: ', datetime.now())
        return super(ResultsDetail, self).get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        context = super(ResultsDetail, self).get_context_data(**kwargs)
        helper.recalc_global_pstats(kwargs['tevent'].id)
        return self.render_to_response(context=context)
