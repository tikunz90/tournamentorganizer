from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from ..models.Tournament import Tournament, TournamentEvent, TournamentStateType
from ..models.Series import Season
from ..models.Team import Team

from beachhandball_app import static_views


class StructureSetupDetail(LoginRequiredMixin, DetailView):
    model = TournamentEvent
    template_name = 'beachhandball/tournamentevent/structure_setup.html'
    login_url = '/login/'
    redirect_field_name = 'structure_setup'

    def get_context_data(self, **kwargs):
        tevent = kwargs["object"]
        kwargs = static_views.getContext(self.request)
        kwargs['tournaments_active'] = 'active_detail'
        kwargs['segment'] = 'structure_setup'
        kwargs['segment_title'] = 'Structure Setup \ ' + tevent.name_short

        kwargs['ts_types'] = TournamentStateType.objects.filter(tournament_event=tevent)
        kwargs['teams_appending'] = []#Team.objects.filter(tournament=tevent)

        return super(StructureSetupDetail, self).get_context_data(**kwargs)