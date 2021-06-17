from beachhandball_app.models.Player import Player
from django.db.models.query import Prefetch
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from ..models.Tournaments import Tournament, TournamentEvent
from ..models.Series import Season
from ..models.Team import Coach, Team

from beachhandball_app import static_views


class TeamsSetupDetail(LoginRequiredMixin, DetailView):
    #model = TournamentEvent
    queryset = TournamentEvent.objects.select_related("tournament")
    template_name = 'beachhandball/tournamentevent/teams_setup.html'
    login_url = '/login/'
    redirect_field_name = 'teams_setup'

    def get_context_data(self, **kwargs):
        tevent = kwargs["object"]
        kwargs = static_views.getContext(self.request)

        teams = Team.objects.select_related("tournament_event", "category").prefetch_related(
            Prefetch("player_set", queryset=Player.objects.select_related("tournament_event__category", "position"), to_attr="players"),
            Prefetch("coach_set", queryset=Coach.objects.select_related("tournament_event__category"), to_attr="coaches")
            )
        kwargs['tournaments_active'] = 'active_detail'
        kwargs['segment'] = 'teams_setup'
        kwargs['segment_title'] = 'Teams Setup \ ' + tevent.name_short

        kwargs["tevent"] = tevent
        kwargs['teams_accepted'] =[team for team in teams if not team.is_dummy and team.tournament_event.id == tevent.id]# teams.all()
        kwargs['teams_appending'] = []#Team.objects.filter(tournament=tevent)

        return super(TeamsSetupDetail, self).get_context_data(**kwargs)