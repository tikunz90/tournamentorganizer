import json
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models.query import Prefetch
from beachhandball_app.models.choices import GAMESTATE_CHOICES
import os
import mimetypes
from django.db import connection
from django.http.response import Http404, HttpResponse
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic.base import View
from beachhandball_app import helper
from beachhandball_app.models.Player import PlayerStats
from datetime import datetime
from beachhandball_app.models.Game import Game
from beachhandball_app.models.Game import Game
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.messages.views import SuccessMessageMixin
from django.conf import settings
from django.forms import modelformset_factory

from beachhandball_app.helper import reverse_querystring, calculate_tstate
from beachhandball_app.game_report import helper_game_report

from beachhandball_app.static_views import checkLoginIsValid, getContext

from bootstrap_modal_forms.generic import BSModalCreateView, BSModalDeleteView, BSModalUpdateView

from ..models.Tournaments import Court, Tournament, TournamentEvent, TournamentStage, TournamentState, TournamentTeamTransition
from ..models.Series import Season
from ..models.Team import Team, TeamStats

from beachhandball_app.forms.structure_setup.forms import GameUpdateForm, GameUpdateResultForm, TTTUpdateForm, TeamStatsUpdateInitialTeamForm, TournamentStageForm, TournamentStateFinishForm, TournamentStateForm, TournamentStateUpdateForm, TeamStatsUpdateTeamForm, GameForm

from beachhandball_app import static_views

#class StructureSetupDetail(LoginRequiredMixin, DetailView):
class StructureSetupDetail(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    #model = TournamentEvent
    queryset = TournamentEvent.objects.select_related("tournament","category")
    template_name = 'beachhandball/tournamentevent/structure_setup.html'
    login_url = '/login/'
    redirect_field_name = 'structure_setup'

    def dispatch(self, request, *args, **kwargs):
        context = getContext(self.request)
        if not checkLoginIsValid(context['gbo_user']):
            return redirect('login')
        self.kwargs['context_data'] = context
        return super(StructureSetupDetail, self).dispatch(request, *args, **kwargs)

    
    def post(self, request, *args, **kwargs):
        pk = kwargs.pop('pk')
        tevent = TournamentEvent.objects.get(id=pk)
        context = self.kwargs["context_data"]
        #tstat_forms = context["tstat_forms"]
        
        TeamStatFormSet = modelformset_factory(TeamStats, TeamStatsUpdateInitialTeamForm, extra=0)
        fs = TeamStatFormSet(self.request.POST, form_kwargs={'tevent': tevent}, queryset=TeamStats.objects.filter(tournamentstate_id=25))
        fs.is_valid()
        objs = fs.save(commit=False)
        print('')
        return super(StructureSetupDetail, self).post(request, *args, **kwargs)
        return reverse("structure_setup.detail", kwargs={"pk": tevent.id})

    def get_context_data(self, **kwargs):
        print('Enter StructureSetupDetail: ', datetime.now())

        #tourn = context['tourn']

        tevent = kwargs["object"]
        #t = Tournament.objects.get(id=1)
        
        context = self.kwargs['context_data']#getContext(self.request)

        #tevent = TournamentEvent.objects.filter(tournament=context['tourn']).select_related('TournamentStages')
        #stages = TournamentStage.objects.filter(tournament_event=tevent).all().prefetch_related('tournament_state_set')
        #prefTeamStats = Prefetch("teamstats_set", queryset=TeamStats.objects.all(), to_attr="tstats")
        #pref=Prefetch("tournamentstate_set", queryset=TournamentState.objects.filter(is_final=False).prefetch_related(prefTeamStats), to_attr="sstates")
        #print(len(connection.queries))
        stages = TournamentStage.objects.select_related("tournament_event").prefetch_related(
            Prefetch("tournamentstate_set", queryset=TournamentState.objects.select_related("tournament_event__category").prefetch_related(
                Prefetch("teamstats_set", queryset=TeamStats.objects.select_related("team").all(), to_attr="stats"),
                Prefetch("game_set", queryset=Game.objects.all(), to_attr="games"),
                Prefetch("ttt_origin", queryset=TournamentTeamTransition.objects.select_related("origin_ts_id", "target_ts_id").all(), to_attr="ttt_origin_pre")
                )
                , to_attr="tstates")
                )

        
        #for stage in stages:
        #    print(stage)
        #    print("################")
        #    for state in stage.tstates:
        #        print(state)
        #        print("-----STATS-----")
        #        for ts in state.stats:
        #            print(ts)
        #        print("-----GAMES-----")
        #        for g in state.games:
        #            print(g)
        print(len(connection.queries))
        #print(stages.query)
        tstages_pre = []
        tstates_pre = []
        for stage in stages:
            if stage.tournament_event.id==tevent.id:
                tstates = []
                for state in stage.tstates:
                    if not state.is_final:
                        tstates.append(state)
                        tstates_pre.append(state)
                stage.tstates_wo_final = tstates
                tstages_pre.append(stage)

        kwargs['tstages_pre'] = tstages_pre#[stage for stage in stages if stage.tournament_event.id==tevent.id]
        
        TeamStatFormSet = modelformset_factory(TeamStats, TeamStatsUpdateInitialTeamForm, extra=0)
        tstat_forms = {}
        for stage in tstages_pre:
            for state in stage.tstates:
                
                tstat_forms[state.id] = TeamStatFormSet(form_kwargs={'tevent': tevent}, queryset=TeamStats.objects.filter(tournamentstate=state))
        kwargs['tstat_forms'] = tstat_forms
        
        kwargs['tourn'] = context['tourn']
        #kwargs['tst_view'] = tevent.tournamentstage_set.all()

        kwargs['tevent'] = tevent

        #kwargs = static_views.getContext(self.request)
        kwargs['tournaments_active'] = 'active_detail'
        kwargs['segment'] = 'structure_setup'
        kwargs['segment_title'] = 'Structure Setup \ ' + tevent.name_short + ' ' + tevent.category.name + ' ' + tevent.category.classification

        #kwargs['ts_types'] = TournamentStage.objects.filter(tournament_event=tevent)
        kwargs['teams_appending'] = []#Team.objects.filter(tournament=tevent)
        
        print('Before check: ', datetime.now())
        helper.check_all_tournamentstate_finshed(tevent, tstates_pre)
        
        #tstate = TournamentState.objects.get(id=6)
       # kwargs['form_tstate'] = TournamentStateUpdateForm(instance=tstate)
        print('Leave StructureSetupDetail: ', datetime.now())
        return super(StructureSetupDetail, self).get_context_data(**kwargs)
    
    def test_func(self):
        return self.request.user.groups.filter(name='tournament_organizer').exists()


class TournamentEventDetail(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = TournamentEvent
    template_name = 'beachhandball/tournamentevent/tevent_printview.html'
    login_url = '/login/'
    redirect_field_name = 'structure_setup'

    def dispatch(self, request, *args, **kwargs):
        context = getContext(self.request)
        if not checkLoginIsValid(context['gbo_user']):
            return redirect('login')
        self.kwargs['context_data'] = context
        return super(TournamentEventDetail, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        print('Enter TournamentEventDetail: ', datetime.now())
        tevent = kwargs["object"]
        context = self.kwargs['context_data']

        kwargs['tourn'] = context['tourn']
        kwargs['tevent'] = tevent

        stages = TournamentStage.objects.select_related("tournament_event").prefetch_related(
            Prefetch("tournamentstate_set", queryset=TournamentState.objects.select_related("tournament_event__category").prefetch_related(
                Prefetch("teamstats_set", queryset=TeamStats.objects.select_related("team").all(), to_attr="stats"),
                Prefetch("game_set", queryset=Game.objects.all(), to_attr="games"),
                Prefetch("ttt_origin", queryset=TournamentTeamTransition.objects.select_related("origin_ts_id", "target_ts_id").all(), to_attr="ttt_origin_pre")
                )
                , to_attr="tstates")
                )

        tstages_pre = []
        tstates_pre = []
        for stage in stages:
            if stage.tournament_event.id==tevent.id:
                tstates = []
                for state in stage.tstates:
                    if not state.is_final:
                        tstates.append(state)
                        tstates_pre.append(state)
                stage.tstates_wo_final = tstates
                tstages_pre.append(stage)

        kwargs['tstages_pre'] = tstages_pre#[stage for stage in stages if stage.tournament_event.id==tevent.id]
        
        #kwargs['tst_view'] = tevent.tournamentstage_set.all()

        #kwargs['tevent'] = tevent

        #kwargs = static_views.getContext(self.request)
        kwargs['tournaments_active'] = 'active_detail'
        kwargs['segment'] = 'structure_setup'
        kwargs['segment_title'] = 'Structure Setup \ '

        #kwargs['ts_types'] = TournamentStage.objects.filter(tournament_event=tevent)
        kwargs['teams_appending'] = []#Team.objects.filter(tournament=tevent)

        return super(TournamentEventDetail, self).get_context_data(**kwargs)
    
    def test_func(self):
        return self.request.user.groups.filter(name='tournament_organizer').exists()
class TournamentStageDetail(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    #model = TournamentStage
    queryset = TournamentStage.objects.select_related("tournament_event").prefetch_related(
            Prefetch("tournamentstate_set", queryset=TournamentState.objects.select_related("tournament_event__category").prefetch_related(
                Prefetch("teamstats_set", queryset=TeamStats.objects.select_related("team").all(), to_attr="stats"),
                Prefetch("game_set", queryset=Game.objects.all(), to_attr="games"),
                Prefetch("ttt_origin", queryset=TournamentTeamTransition.objects.select_related("origin_ts_id", "target_ts_id").all(), to_attr="ttt_origin_pre")
                )
                , to_attr="tstates")
                )
    template_name = 'beachhandball/tournamentevent/tstage_printview.html'
    login_url = '/login/'
    redirect_field_name = 'structure_setup'

    def dispatch(self, request, *args, **kwargs):
        context = getContext(self.request)
        if not checkLoginIsValid(context['gbo_user']):
            return redirect('login')
        self.kwargs['context_data'] = context
        return super(TournamentStageDetail, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        print('Enter TournamentStageDetail: ', datetime.now())
        tstage = kwargs["object"]
        context = self.kwargs['context_data']

        kwargs['tourn'] = context['tourn']

        
        tstates = []
        for state in tstage.tstates:
            if not state.is_final:
                tstates.append(state)
        tstage.tstates_wo_final = tstates
        kwargs['tstage'] = tstage
        #kwargs['tst_view'] = tevent.tournamentstage_set.all()

        #kwargs['tevent'] = tevent

        #kwargs = static_views.getContext(self.request)
        kwargs['tournaments_active'] = 'active_detail'
        kwargs['segment'] = 'structure_setup'
        kwargs['segment_title'] = 'Structure Setup \ '

        #kwargs['ts_types'] = TournamentStage.objects.filter(tournament_event=tevent)
        kwargs['teams_appending'] = []#Team.objects.filter(tournament=tevent)

        return super(TournamentStageDetail, self).get_context_data(**kwargs)
    
    def test_func(self):
        return self.request.user.groups.filter(name='tournament_organizer').exists()

class StageCreateView(BSModalCreateView):
    template_name = 'beachhandball/tournamentevent/create_stage_form.html'
    form_class = TournamentStageForm
    success_message = 'Success: Stage was created.'

    def get_context_data(self, **kwargs):
        context = super(StageCreateView, self).get_context_data(**kwargs)
        tevent = get_object_or_404(TournamentEvent, id=self.kwargs.get('pk'))

        context['form'].fields['tournament_event'].queryset = TournamentEvent.objects.filter(id=tevent.id)
        return context

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

    def get_context_data(self, **kwargs):
        context = super(StateCreateView, self).get_context_data(**kwargs)
        tstage = get_object_or_404(TournamentStage, id=self.kwargs.get('pk_tstage'))

        context['form'].fields['tournament_stage'].queryset = TournamentStage.objects.filter(id=tstage.id)
        return context

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
           return reverse_querystring("structure_setup.detail", kwargs={"pk": pk}, query_kwargs={'tab': self.kwargs["pk_tstage"], 'tab_tstate': 0})

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


class StateFinishView(BSModalUpdateView):
    model = TournamentState
    template_name = 'beachhandball/templates/finish_tstate_form.html'
    form_class = TournamentStateFinishForm
    success_message = 'Success: State was updated.'

    def get_context_data(self, **kwargs):
        print('Enter StateFinishView: ', datetime.now())
        tstate = self.object
        kwargs['tevent'] = tstate.tournament_event 
        kwargs['ttt']  = TournamentTeamTransition.objects.filter(origin_ts_id=tstate).order_by('origin_rank')
        kwargs['teamstats']  = TeamStats.objects.filter(tournament_event=tstate.tournament_event, tournamentstate=tstate).order_by('-ranking_points')
        print('Leave StateFinishView: ', datetime.now())
        return super(StateFinishView, self).get_context_data(**kwargs)

    
    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        tevent = get_object_or_404(TournamentEvent, id=self.kwargs.get('pk_tevent'))
        tstage = get_object_or_404(TournamentStage, id=self.kwargs.get('pk_tstage'))
        form.instance.tournament_event = tevent
        form.instance.tournament_stage = tstage

        helper.check_tournamentstate_finished(tevent, self.object)
        return super().form_valid(form)

    def get_success_url(self):
           pk = self.kwargs["pk_tevent"]
           return reverse_querystring("structure_setup.detail", kwargs={"pk": pk}, query_kwargs={'tab': self.kwargs["pk_tstage"]})


class TeamStatsUpdateTeamView(BSModalUpdateView):
    model = TeamStats
    template_name = 'beachhandball/templates/update_teamstat_form.html'
    form_class = TeamStatsUpdateTeamForm
    success_message = 'Success: TeamStat was updated.'

    def get_context_data(self, **kwargs):
        tstat = self.object
        context = super(TeamStatsUpdateTeamView, self).get_context_data(**kwargs)
        
        teams = Team.objects.filter(tournament_event=tstat.tournament_event, is_dummy=False)
        context['form'].fields['team'].queryset = teams
        return context
    
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

    def get_context_data(self, **kwargs):
        ttt = self.object
        context = super(TTTUpdateView, self).get_context_data(**kwargs)
        
        ttts = TournamentState.objects.filter(tournament_event=ttt.tournament_event,
        hierarchy__gt=ttt.origin_ts_id.hierarchy)
        context['form'].fields['target_ts_id'].queryset = ttts
        return context
    
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
    template_name = 'beachhandball/templates/update_game_form.html'
    form_class = GameUpdateForm
    success_message = 'Success: Game was updated.'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(GameUpGameView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(GameUpGameView, self).post(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        # here you can make your custom validation for any particular user
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        game = self.object
        context = super(GameUpGameView, self).get_context_data(**kwargs)
        
        tstate = game.tournament_state
        qTeamStats = TeamStats.objects.filter(tournamentstate=tstate)
        qTeams = Team.objects.filter(is_dummy=False)
        context['form'].fields['court'].queryset = Court.objects.filter(tournament=game.tournament)
        context['form'].fields['team_st_a'].queryset = qTeamStats
        context['form'].fields['team_st_b'].queryset = qTeamStats
        #context['form'].fields['team_a'].queryset = qTeams
        #context['form'].fields['team_b'].queryset = qTeams
        return context
    
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
           from_gameplan = self.kwargs["from_gameplan"]
           if from_gameplan == 1:
               return reverse_lazy('game_plan')
           return reverse_querystring("structure_setup.detail", kwargs={"pk": pk}, query_kwargs={'tab': self.kwargs["pk_tstage"], 'tab_tstate': 0})


class DownloadPreGameView(View):
    # Set the content type value
    content_type_value = 'text/plain'

    def get(self, request, pk, pk_tevent, pk_tstage):
        game = Game.objects.get(id=pk)
        if game:
            # Define the full file path
            filepath, filename = helper_game_report.create_pregame_report_excel(game)

            if os.path.exists(filepath):
                # Open the file for reading content
                path = open(filepath, 'rb')
                # Set the mime type
                mime_type, _ = mimetypes.guess_type(filepath)
                # Set the return value of the HttpResponse
                response = HttpResponse(path, content_type=mime_type)
                # Set the HTTP header for sending to browser
                response['Content-Disposition'] = "attachment; filename=%s" % filename
                # Return the response value
                return response
            else:
                raise Http404
            #with open(file_path, 'rb') as fh:
            #    response = HttpResponse(
            #        fh.read(),
            #        content_type=self.content_type_value
            #    )
            #    response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            #return response
        else:
            raise Http404

    def get_success_url(self):
           pk = self.kwargs["pk_tevent"]
           return reverse_querystring("structure_setup.detail", kwargs={"pk": pk}, query_kwargs={'tab': self.kwargs["pk_tstage"], 'tab_tstate': 0})

class DownloadPreGameAllView(View):
    # Set the content type value
    content_type_value = 'text/plain'

    def get(self, request, pk, pk_tevent, pk_tstage):
        tstate = TournamentState.objects.get(id=pk)
        if tstate:
            # Define the full file path
            filepath, filename = helper_game_report.create_all_tstate_pregame_report_excel(tstate)

            if os.path.exists(filepath):
                # Open the file for reading content
                path = open(filepath, 'rb')
                # Set the mime type
                mime_type, _ = mimetypes.guess_type(filepath)
                # Set the return value of the HttpResponse
                response = HttpResponse(path, content_type=mime_type)
                # Set the HTTP header for sending to browser
                response['Content-Disposition'] = "attachment; filename=%s" % filename
                # Return the response value
                return response
            else:
                raise Http404
            #with open(file_path, 'rb') as fh:
            #    response = HttpResponse(
            #        fh.read(),
            #        content_type=self.content_type_value
            #    )
            #    response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            #return response
        else:
            raise Http404

    def get_success_url(self):
           pk = self.kwargs["pk_tevent"]
           return reverse_querystring("structure_setup.detail", kwargs={"pk": pk}, query_kwargs={'tab': self.kwargs["pk_tstage"], 'tab_tstate': 0})

class GameResultGameView(BSModalUpdateView):
    model = Game
    template_name = 'beachhandball/templates/update_game_result_form.html'
    form_class = GameUpdateResultForm
    success_message = 'Success: GameResult was updated.'
    
    def get_context_data(self, **kwargs):
        game = self.object
        context = super(GameResultGameView, self).get_context_data(**kwargs)
        
        context['pstats_a'] = PlayerStats.objects.filter(tournament_event=game.tournament_event, game=game, player__team=game.team_a, is_ranked=False)
        context['pstats_b'] = PlayerStats.objects.filter(tournament_event=game.tournament_event, game=game, player__team=game.team_b, is_ranked=False)
        return context

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
           from_gameplan = self.kwargs["from_gameplan"]
           if from_gameplan == 1:
               return reverse_lazy('game_plan')
           return reverse_querystring("structure_setup.detail", kwargs={"pk": pk}, query_kwargs={'tab': self.kwargs["pk_tstage"], 'tab_tstate': 0})

def postUpdateGameResult(request, pk_tevent, pk_tstage, pk):
    if request.method == "POST" and request.is_ajax():
        form = GameUpdateResultForm(request.POST, request=request)
        game = get_object_or_404(Game, id=pk)
        tevent = get_object_or_404(TournamentEvent, id=pk_tevent)
        tstage = get_object_or_404(TournamentStage, id=pk_tstage)
        game.tournament_event = tevent
        game.tournament_stage = tstage   
        game.gamestate = GAMESTATE_CHOICES[2][0]
        game.score_team_a_halftime_1 = form.data['score_team_a_halftime_1']
        game.score_team_a_halftime_2 = form.data['score_team_a_halftime_2']
        game.score_team_a_penalty = form.data['score_team_a_penalty']
        game.score_team_b_halftime_1 = form.data['score_team_b_halftime_1']
        game.score_team_b_halftime_2 = form.data['score_team_b_halftime_2']
        game.score_team_b_penalty = form.data['score_team_b_penalty']
        game.save()
        #calculate_tstate(self.object.tournament_state)
        if form.data['upload-data']:
            upload_data = json.loads(form.data['upload-data'])
            helper_game_report.import_playerstats_game_report(game, upload_data)
        return JsonResponse({"success":True, "msg": "OK", "game_id": game.id}, status=200)
    return JsonResponse({"success":False, "msg": "Failed"}, status=400)

class GameDeleteView(BSModalDeleteView):
    model = Game
    template_name = 'beachhandball/tournamentevent/delete_game.html'
    success_message = 'Success: Game was deleted.'

    def get_success_url(self):
           pk = self.kwargs["pk_tevent"]
           return reverse_querystring("structure_setup.detail", kwargs={"pk": pk}, query_kwargs={'tab': self.kwargs["pk_tstage"], 'tab_tstate': 0})


class GameCreateView(BSModalCreateView):
    template_name = 'beachhandball/templates/create_form.html'
    form_class = GameForm
    success_message = 'Success: State was created.'

    def get_context_data(self, **kwargs):
        
        context = super(GameCreateView, self).get_context_data(**kwargs)
        tevent = get_object_or_404(TournamentEvent, id=self.kwargs.get('pk_tevent'))
        tstage = get_object_or_404(TournamentStage, id=self.kwargs.get('pk_tstage'))
        tstate = get_object_or_404(TournamentState, id=self.kwargs.get('pk_tstate'))
        
        context['form'].fields['tournament'].queryset = Tournament.objects.filter(id=tevent.tournament.id)
        context['form'].fields['tournament_event'].queryset = TournamentEvent.objects.filter(id=tevent.id)
        context['form'].fields['team_st_a'].queryset = TeamStats.objects.filter(tournamentstate=tstate)
        context['form'].fields['team_st_b'].queryset = TeamStats.objects.filter(tournamentstate=tstate)
        context['form'].fields['tournament_state'].queryset = TournamentState.objects.filter(id=tstate.id)
        context['form'].fields['court'].queryset = Court.objects.filter(tournament=tevent.tournament)
        return context

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
        return reverse_querystring("structure_setup.detail", kwargs={"pk": pk}, query_kwargs={'tab': self.kwargs["pk_tstage"], 'tab_tstate': 0})

@login_required(login_url="/login/")
@user_passes_test(lambda u: u.groups.filter(name='tournament_organizer').exists(),
login_url="/login/", redirect_field_name='next')
def update_teamsetup(request, pk_tevent, pk_tstage, pk_tstate):
    context = getContext(request)
    if not checkLoginIsValid(context['gbo_user']):
        return redirect('login')

    tevent = TournamentEvent.objects.get(id=pk_tevent)
    #helper.update_user_tournament_events(context['gbo_user'], context['tourn'])
    
    context['segment'] = 'index'
    context['segment_title'] = 'Overview'

    #html_template = loader.get_template( 'index.html' )
    #return HttpResponse(html_template.render(context, request))
    if request.method == 'POST':
        TeamStatFormSet = modelformset_factory(TeamStats, TeamStatsUpdateInitialTeamForm, extra=0)
        
        #tstat_forms = context["tstat_forms"]
        
        
        fs = TeamStatFormSet(request.POST, form_kwargs={'tevent': tevent}, queryset=TeamStats.objects.filter(tournamentstate_id=pk_tstate))
        print(fs.is_valid())
        if fs.is_valid():
            objs = fs.save(commit=True)
            for obj in objs:
                print(obj)
    return redirect(reverse("structure_setup.detail", kwargs={"pk": pk_tevent}))