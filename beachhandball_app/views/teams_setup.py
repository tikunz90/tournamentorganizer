from django.views.generic.detail import DetailView

from ..models.Tournament import Tournament, TournamentEvent
from ..models.Series import Season
from ..models.Team import Team


class TeamsSetupDetail(DetailView):
    model = TournamentEvent
    template_name = 'beachhandball/tournamentevent/teams_setup.html'

    def get_context_data(self, **kwargs):
        tevent = kwargs["object"]
        kwargs['tournaments_active'] = 'active_detail'
        kwargs['segment'] = 'teams_setup'
        kwargs['segment_title'] = 'Teams Setup \ ' + tevent.name_short
        kwargs['act_season'] = Season.objects.filter(is_actual=True).first()
        t = Tournament.objects.get(id=1)
        kwargs['tourn'] = t
        kwargs['events'] = TournamentEvent.objects.filter(tournament=t)

        kwargs['teams_accepted'] = Team.objects.filter(tournament=tevent)
        kwargs['teams_appending'] = Team.objects.filter(tournament=tevent)

        return super(TeamsSetupDetail, self).get_context_data(**kwargs)