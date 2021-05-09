from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse, JsonResponse
from django import template

from authentication.models import GBOUser
from ..models.Tournament import Tournament, TournamentEvent, TournamentState
from ..models.Team import Team, TeamStats
from ..models.Series import Season
from ..models.Game import Game


def games_list(request, pk_tstate):
    data = dict()
    if request.method == 'GET':
        tstate = TournamentState.objects.get(id=pk_tstate)
        games = Game.objects.filter(tournament_state=tstate)

        # asyncSettings.dataKey = 'table'
        data['table'] = loader.render_to_string(
            'beachhandball/tournamentevent/_games_table.html',
            {'games': games,
             'tevent': tstate.tournament_event,
             'stage': tstate.tournament_stage,
            'tstate': tstate},
            request=request
        )
        return JsonResponse(data)