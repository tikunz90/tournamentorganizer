from beachhandball_app.models.choices import GAMESTATE_CHOICES
import os
import mimetypes
from django.http.response import Http404, HttpResponse

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
from beachhandball_app.helper import reverse_querystring, calculate_tstate
from beachhandball_app.game_report import create_game_report

from beachhandball_app.static_views import checkLoginIsValid, getContext

from bootstrap_modal_forms.generic import BSModalCreateView, BSModalDeleteView, BSModalUpdateView

from ..models.Tournaments import Court, Tournament, TournamentEvent, TournamentStage, TournamentState, TournamentTeamTransition
from ..models.Series import Season
from ..models.Team import Team, TeamStats

from beachhandball_app.forms.structure_setup.forms import GameUpdateForm, GameUpdateResultForm, TTTUpdateForm, TournamentStageForm, TournamentStateFinishForm, TournamentStateForm, TournamentStateUpdateForm, TeamStatsUpdateTeamForm, GameForm

from beachhandball_app import static_views

#class StructureSetupDetail(LoginRequiredMixin, DetailView):
class StructureSetupDetail(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = TournamentEvent
    template_name = 'beachhandball/tournamentevent/structure_setup.html'
    login_url = '/login/'
    redirect_field_name = 'structure_setup'

    def dispatch(self, request, *args, **kwargs):
        context = getContext(self.request)
        if not checkLoginIsValid(context['gbo_user']):
            return redirect('login')
        self.kwargs['context_data'] = context
        return super(StructureSetupDetail, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        print('Enter StructureSetupDetail: ', datetime.now())

        #tourn = context['tourn']

        tevent = kwargs["object"]
        #t = Tournament.objects.get(id=1)
        
        context = self.kwargs['context_data']#getContext(self.request)

        tevent = TournamentEvent.objects.filter(tournament=context['tourn']).select_related('TournamentStages')
        stages = TournamentStage.objects.filter(tournament_event=tevent).all().prefetch_related('tournament_state_set')
        print(stages.query)
        kwargs['tstages_pre'] = [stage for stage in tevent.tournament_stage_set.all()]
        kwargs['tourn'] = context['tourn']
        kwargs['tst_view'] = tevent.tournamentstage_set.all()

        kwargs['tevent'] = tevent

        #kwargs = static_views.getContext(self.request)
        kwargs['tournaments_active'] = 'active_detail'
        kwargs['segment'] = 'structure_setup'
        kwargs['segment_title'] = 'Structure Setup \ ' + tevent.name_short

        kwargs['ts_types'] = TournamentStage.objects.filter(tournament_event=tevent)
        kwargs['teams_appending'] = []#Team.objects.filter(tournament=tevent)
        
        print('Before check: ', datetime.now())
        helper.check_all_tournamentstate_finshed(tevent)
        
        #tstate = TournamentState.objects.get(id=6)
       # kwargs['form_tstate'] = TournamentStateUpdateForm(instance=tstate)
        print('Leave StructureSetupDetail: ', datetime.now())
        return super(StructureSetupDetail, self).get_context_data(**kwargs)
    
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
           return reverse_querystring("structure_setup.detail", kwargs={"pk": pk}, query_kwargs={'tab': self.kwargs["pk_tstage"], 'tab_tstate': 0})


class DownloadPreGameView(View):
    # Set the content type value
    content_type_value = 'text/plain'

    def get(self, request, pk, pk_tevent, pk_tstage):
        game = Game.objects.get(id=pk)
        if game:
            # Define the full file path
            filepath, filename = create_game_report.create_pregame_report_excel(game)

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
            filepath, filename = create_game_report.create_all_tstate_pregame_report_excel(tstate)

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
        
        context['pstats_a'] = PlayerStats.objects.filter(teamstat=game.team_st_a)
        context['pstats_b'] = PlayerStats.objects.filter(teamstat=game.team_st_b)
        return context

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        tevent = get_object_or_404(TournamentEvent, id=self.kwargs.get('pk_tevent'))
        tstage = get_object_or_404(TournamentStage, id=self.kwargs.get('pk_tstage'))
        form.instance.tournament_event = tevent
        form.instance.tournament_stage = tstage
        self.object.gamestate = GAMESTATE_CHOICES[2][0]
        self.object.save()
        #calculate_tstate(self.object.tournament_state)
        return super().form_valid(form)

    def get_success_url(self):
           pk = self.kwargs["pk_tevent"]
           return reverse_querystring("structure_setup.detail", kwargs={"pk": pk}, query_kwargs={'tab': self.kwargs["pk_tstage"], 'tab_tstate': 0})

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
