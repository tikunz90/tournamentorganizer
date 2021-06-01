from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from ..models.Tournaments import Tournament, TournamentEvent
from ..models.Series import Season
from ..models.Team import Team

from beachhandball_app import static_views


class TeamsSetupDetail(LoginRequiredMixin, DetailView):
    model = TournamentEvent
    template_name = 'beachhandball/tournamentevent/teams_setup.html'
    login_url = '/login/'
    redirect_field_name = 'teams_setup'

    def get_context_data(self, **kwargs):
        tevent = kwargs["object"]
        kwargs = static_views.getContext(self.request)
        kwargs['tournaments_active'] = 'active_detail'
        kwargs['segment'] = 'teams_setup'
        kwargs['segment_title'] = 'Teams Setup \ ' + tevent.name_short

        kwargs["tevent"] = tevent
        kwargs['teams_accepted'] = []#Team.objects.filter(tournament=tevent)
        kwargs['teams_appending'] = []#Team.objects.filter(tournament=tevent)

        return super(TeamsSetupDetail, self).get_context_data(**kwargs)