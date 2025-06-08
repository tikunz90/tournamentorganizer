from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models.query import Prefetch
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django import template
from django.contrib import messages

from authentication.models import GBOUser
from beachhandball_app import helper_structure
from beachhandball_app import helper
from ..models.Tournaments import Tournament, TournamentEvent, TournamentState
from ..models.Team import Team, TeamStats
from ..models.Series import Season
from ..models.Game import Game


def games_list(request, pk_tstate):
    data = dict()
    if request.method == 'GET':
        tstate = TournamentState.objects.prefetch_related(
            Prefetch("game_set", queryset=Game.objects.all(), to_attr="games")
        ).get(id=pk_tstate)
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

@login_required(login_url="/login/")
@user_passes_test(lambda u: u.groups.filter(name='tournament_organizer').exists(),
login_url="/login/", redirect_field_name='structure_setup')
def tstate_add_team(request, pk_tstage, pk_tevent, pk):
    context = helper.getContext(request)
    if not helper.checkLoginIsValid(context['gbo_user']):
        return redirect('login')
    for te in context['events']:
        if te.id == pk_tevent:
            context['tevent'] = te
            break
    context['segment'] = 'structure_setup'
    context['segment_title'] = 'Structure Setup'

    context['pk_tstage'] = pk_tstage
    context['pk'] = pk

    if request.method == 'POST':
        print('Delete team')
        
        result = helper_structure.tstate_add_team(pk_tevent, pk, int(request.POST['num_new_teams']))
        msg_type = messages.INFO
        if result['isError'] == True:
            msg_type = messages.ERROR
        messages.add_message(request, msg_type, result['msg'])
        return HttpResponseRedirect(reverse("structure_setup.detail", kwargs={"pk": pk_tevent}))
    elif request.method == 'GET':
        html_template = loader.get_template( 'beachhandball/tournamentevent/add_state_team.html' )
        return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
@user_passes_test(lambda u: u.groups.filter(name='tournament_organizer').exists(),
login_url="/login/", redirect_field_name='structure_setup')
def tstate_delete_team(request, pk_tstage, pk_tevent, pk):
    context = helper.getContext(request)
    if not helper.checkLoginIsValid(context['gbo_user']):
        return redirect('login')
    for te in context['events']:
        if te.id == pk_tevent:
            context['tevent'] = te
            break
    context['segment'] = 'structure_setup'
    context['segment_title'] = 'Structure Setup'

    context['pk_tstage'] = pk_tstage
    context['pk'] = pk

    if request.method == 'POST':
        print('Delete team')
        result = helper_structure.tstate_delete_team(pk_tevent, pk)
        msg_type = messages.INFO
        if result['isError'] == True:
            msg_type = messages.ERROR
        messages.add_message(request, msg_type, result['msg'])
        return HttpResponseRedirect(reverse("structure_setup.detail", kwargs={"pk": pk_tevent}))
    elif request.method == 'GET':
        html_template = loader.get_template( 'beachhandball/tournamentevent/delete_state_team.html' )
        return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
@user_passes_test(lambda u: u.groups.filter(name='tournament_organizer').exists(),
login_url="/login/", redirect_field_name='structure_setup')
def delete_structure(request, pk_tevent):
    context = helper.getContext(request)
    if not helper.checkLoginIsValid(context['gbo_user']):
        return redirect('login')
    for te in context['events']:
        if te.id == pk_tevent:
            context['tevent'] = te
            break
    context['segment'] = 'structure_setup'
    context['segment_title'] = 'Structure Setup'

    if request.method == 'POST':
        print('Delete all strucutre')
        TournamentState.objects.filter(tournament_event=context['tevent'], is_final=True).delete()
        TournamentStage.objects.filter(tournament_event=context['tevent']).delete()
        return HttpResponseRedirect(reverse("structure_setup.detail", kwargs={"pk": pk_tevent}))
    elif request.method == 'GET':
        html_template = loader.get_template( 'beachhandball/tournamentevent/delete_structure_confirmation.html' )
        return HttpResponse(html_template.render(context, request))