# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from django.urls import reverse
from beachhandball_app.tasks import update_user_tournament_events_async
from datetime import datetime
import time
import json
from django.db.models.query import Prefetch
from django.forms.models import model_to_dict
from rest_framework.renderers import JSONRenderer
from django.utils.dateparse import parse_datetime

from django.views.generic import TemplateView
from beachhandball_app import helper, wizard
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django import template
from django.db.models import Q

from authentication.models import GBOUser
from .models.Tournaments import Court, Referee, Tournament, TournamentEvent, TournamentSettings, TournamentStage, TournamentState
from .models.Team import Team, TeamStats
from .models.Series import Season
from .models.Game import Game
from beachhandball_app.forms.basic_setup.forms import CourtForm, TournamentSettingsForm
from beachhandball_app.api.serializers.game import GameSerializer,GameRunningSerializer, serialize_game
from beachhandball_app.game_report import create_game_report
from .services.services import SWS

def getContext(request):
    print('Enter getContext' , datetime.now())
    context = {}

    guser = GBOUser.objects.filter(user=request.user).first()
    
    if guser is None:
        return context
    else:
        context['gbo_user'] = guser
        context['season_active'] = guser.season_active['name'] #SWS.getSeasonActive(guser)
        context['token'] = guser.token
    
    t = Tournament.objects.prefetch_related(
        Prefetch("tournamentsettings_set", queryset=TournamentSettings.objects.all(), to_attr="settings"), 
        Prefetch("tournamentevent_set", queryset=TournamentEvent.objects.all(), to_attr="events")).get(organizer=guser.subject_id, is_active=True)
    context['tourn'] = t
    context['tourn_settings'] = t.settings[0] #TournamentSettings.objects.get(tournament=t)
    context['events'] = t.events #TournamentEvent.objects.filter(tournament=t)
    print('Exit getContext', datetime.now())
    return context

def checkLoginIsValid(gbouser):
    if not gbouser.is_online:
        return True
    if int(time.time()) > time.mktime(gbouser.validUntil.timetuple()):
        return False
    else:
        return True

def getData(request):
    t = Tournament.objects.get(id=1)
    tevent = TournamentEvent.objects.filter(tournament=t).first();
    tstates = list(TournamentState.objects.filter(tournament_event=tevent).values())

    for ts in tstates:
        tstats = TeamStats.objects.filter(tournamentstate=ts['id'])
        ts['tstats'] = list(tstats.values())
        for stat in ts['tstats']:
            team = Team.objects.filter(id=stat['team_id']).first()
            stat['team_name'] = team.name
    data = {
        'teams': list(Team.objects.all().filter(tournament_event=tevent).values()),
        'tstates': tstates
    }
    

    return JsonResponse(data)

@login_required(login_url="/login/")
def UpdateGameFromList(request):
    t = Tournament.objects.get(id=1)
    tevent = TournamentEvent.objects.filter(tournament=t).first();
    tstates = list(TournamentState.objects.filter(tournament_event=tevent).values())

    if request.GET:
        data = {
            'game': list()
        }
        return JsonResponse(data)


@method_decorator(login_required, name='dispatch')
class UpdateGameFromList(TemplateView):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(UpdateGameFromList, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = {'game': 'Hello World'}
        return JsonResponse(context)
        #return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        game = request.POST['game']
        new_dt = request.POST['datetime']
        dt = parse_datetime(new_dt)
        game_obj = Game.objects.filter(pk=game).update(starttime=dt)
        context = {'game':game, 'new_datetime': new_dt}
        return JsonResponse(context)

@method_decorator(login_required, name='dispatch')
class UpdateGameCourtFromList(TemplateView):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(UpdateGameCourtFromList, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = {'game': 'Hello World'}
        return JsonResponse(context)
        #return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        game = request.POST['game']
        new_c = request.POST['new_court']
        court = Court.objects.get(id=new_c)
        game_obj = Game.objects.filter(pk=game).update(court=court)
        context = {'game':game, 'court': court.name}
        return JsonResponse(context)

def not_in_student_group(user):
    if user:
        return user.groups.filter(name='tournament_organizer').count() == 0
    return False

@login_required(login_url="/login/")
@user_passes_test(lambda u: u.groups.filter(name='tournament_organizer').exists(),
login_url="/login/", redirect_field_name='next')
def index(request):
    context = getContext(request)
    if not checkLoginIsValid(context['gbo_user']):
        return redirect('login')
    
    context['segment'] = 'index'
    context['segment_title'] = 'Overview'

    html_template = loader.get_template( 'index.html' )
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
@user_passes_test(lambda u: u.groups.filter(name='tournament_organizer').exists(),
login_url="/login/", redirect_field_name='next')
def setup_wizard(request, pk_tevent):
    context = getContext(request)
    if not checkLoginIsValid(context['gbo_user']):
        return redirect('login')
    for te in context['events']:
        if te.id == pk_tevent:
            context['tevent'] = te
            break
    context['segment'] = 'index'
    context['segment_title'] = 'Overview'

    if request.method == 'POST':
        structure_data = json.loads(request.POST['structure-data'])
        result = wizard.wizard_create_structure(te, structure_data)
        return HttpResponseRedirect(reverse("structure_setup.detail", kwargs={"pk": pk_tevent}))

    html_template = loader.get_template( 'forms-setup-wizard.html' )
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
@user_passes_test(lambda u: u.groups.filter(name='tournament_organizer').exists(),
login_url="/login/", redirect_field_name='structure_setup')
def delete_structure(request, pk_tevent):
    context = getContext(request)
    if not checkLoginIsValid(context['gbo_user']):
        return redirect('login')
    for te in context['events']:
        if te.id == pk_tevent:
            context['tevent'] = te
            break
    context['segment'] = 'structure_setup'
    context['segment_title'] = 'Structure Setup'

    if request.method == 'POST':
        print('Delete all strucutre')
        TournamentStage.objects.filter(tournament_event=context['tevent']).delete()
        return HttpResponseRedirect(reverse("structure_setup.detail", kwargs={"pk": pk_tevent}))
    elif request.method == 'GET':
        html_template = loader.get_template( 'beachhandball/tournamentevent/delete_structure_confirmation.html' )
        return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
@user_passes_test(lambda u: u.groups.filter(name='tournament_organizer').exists(),
login_url="/login/", redirect_field_name='next')
def setup_wizard_gameplan(request):
    context = getContext(request)
    if not checkLoginIsValid(context['gbo_user']):
        return redirect('login')

    context['segment'] = 'game_plan'
    context['segment_title'] = 'Game Plan'

    if request.method == 'POST':
        gameplan_data = json.loads(request.POST['gameplan-data'])
        result = wizard.wizard_create_gameplan(gameplan_data)
        return HttpResponseRedirect(reverse("game_plan"))

    html_template = loader.get_template( 'forms-setup-wizard-gameplan.html' )
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
@user_passes_test(lambda u: u.groups.filter(name='tournament_organizer').exists(),
login_url="/login/", redirect_field_name='structure_setup')
def delete_gameplan(request):
    context = getContext(request)
    if not checkLoginIsValid(context['gbo_user']):
        return redirect('login')

    context['segment'] = 'structure_setup'
    context['segment_title'] = 'Structure Setup'

    if request.method == 'POST':
        print('Delete all games')
        #TournamentStage.objects.filter(tournament_event=context['tevent']).delete()
        return HttpResponseRedirect(reverse("game_plan"))
    elif request.method == 'GET':
        html_template = loader.get_template( 'beachhandball/delete_gameplan_confirmation.html' )
        return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
@user_passes_test(lambda u: u.groups.filter(name='tournament_organizer').exists(),
login_url="/login/", redirect_field_name='next')
def basic_setup(request):
    
    context = getContext(request)
    if not checkLoginIsValid(context['gbo_user']):
        return redirect('login')

    formCourt = None
    context['form_sender'] = ''
    if request.method == 'POST' and request.POST.get('form_sender') == 'tourn_settings':
        context['form_sender'] = 'tourn_settings'
        formCourt = CourtForm()
        form = TournamentSettingsForm(request.POST, instance=context['tourn_settings'])
        if form.is_valid():
            form.save()
    
    if request.method == 'POST' and request.POST.get('form_sender') == 'court_create':
        context['form_sender'] = 'court_create'
        form = TournamentSettingsForm(instance=context['tourn_settings'])
        formCourt = CourtForm(request.POST)
        if formCourt.is_valid():
            formCourt.save()
    
    if request.method == 'GET':
        form = TournamentSettingsForm(instance=context['tourn_settings'])
    if request.method == 'GET' and formCourt is None:
        formCourt = CourtForm()

    context['segment'] = 'basic_setup'
    context['segment_title'] = 'Basic Setup'

    context['tourn_settings_form'] = form
    context['court_form'] = formCourt

    html_template = loader.get_template( 'beachhandball/basic_setup.html' )
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
@user_passes_test(lambda u: u.groups.filter(name='tournament_organizer').exists(),
login_url="/login/", redirect_field_name='next')
def teams_setup(request):
    
    context = getContext(request)
    if not checkLoginIsValid(context['gbo_user']):
        return redirect('login')

    context['segment'] = 'teams_setup'
    context['segment_title'] = 'Teams Setup'

    html_template = loader.get_template( 'beachhandball/teams_setup.html' )
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
@user_passes_test(lambda u: u.groups.filter(name='tournament_organizer').exists(),
login_url="/login/", redirect_field_name='next')
def structure_setup(request):
    
    context = getContext(request)
    if not checkLoginIsValid(context['gbo_user']):
        return redirect('login')

    context['segment'] = 'structure_setup'
    context['segment_title'] = 'Structure Setup'

    html_template = loader.get_template( 'beachhandball/structure_setup.html' )
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
@user_passes_test(lambda u: u.groups.filter(name='tournament_organizer').exists(),
login_url="/login/", redirect_field_name='next')
def game_plan(request):
    
    context = getContext(request)
    if not checkLoginIsValid(context['gbo_user']):
        return redirect('login')

    tourn = context['tourn']
    tevents = context['events']
    tourn_data = Tournament.objects.prefetch_related(
            Prefetch("game_set", queryset=Game.objects.select_related("tournament", "tournament_event__category", "team_a", "team_b", "team_st_a__team", "team_st_b__team", "ref_a", "ref_b", "tournament_state__tournament_stage", "court")
                , to_attr="all_games"),
            Prefetch("tournamentevent_set", queryset=TournamentEvent.objects.select_related("tournament", "category").prefetch_related(
                Prefetch("tournamentstate_set", queryset=TournamentState.objects.select_related("tournament_event__category", "tournament_stage")
                , to_attr="all_tstates")
            )
                , to_attr="all_tevents"),
            Prefetch("court_set", queryset=Court.objects.select_related("tournament")
                , to_attr="all_courts"),
            Prefetch("referee_set", queryset=Referee.objects.select_related("tournament")
                , to_attr="all_refs")
                ).get(id=tourn.id)
    #all_tstates_qs = Q()
    #for event in tevents:
    #    all_tstates_qs = all_tstates_qs | Q(tournament_event=event, is_final=False)
    tstates = []
    for te in tourn_data.all_tevents:
        #print(te.category)
        for ts in te.all_tstates:
            #print(ts.tournament_event.category)
            if ts.is_final is False:
                tstates.append(ts)
    context['tstates'] = tstates #TournamentState.objects.filter(all_tstates_qs)
    context['segment'] = 'game_plan'
    context['segment_title'] = 'Game Plan'

    context['courts'] = tourn_data.all_courts #Court.objects.filter(tournament=tourn)
    context['referees'] = tourn_data.all_refs #Referee.objects.filter(tournament=tourn)

    #data_list = str(JSONRenderer().render(GameSerializer(tourn.game_set.all(), many=True).data), 'utf-8')
    context['games'] = tourn_data.all_games
    for g in tourn_data.all_games:
        print(str(g.tournament_event.category))
    #JSONRenderer().render(GameRunningSerializer(tourn.game_set.all(), many=True).data)

    html_template = loader.get_template( 'beachhandball/game_plan.html' )
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
@user_passes_test(lambda u: u.groups.filter(name='tournament_organizer').exists(),
login_url="/login/", redirect_field_name='next')
def results(request):
    
    context = getContext(request)
    if not checkLoginIsValid(context['gbo_user']):
        return redirect('login')

    context['segment'] = 'results'
    context['segment_title'] = 'Results'

    html_template = loader.get_template( 'beachhandball/tournamentevent/results.html' )
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
@user_passes_test(lambda u: u.groups.filter(name='tournament_organizer').exists(),
login_url="/login/", redirect_field_name='next')
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        
        load_template      = request.path.split('/')[-1]
        context['segment'] = load_template
        context['segment_title'] = load_template.split('.')[0]
        html_template = loader.get_template( load_template )
        return HttpResponse(html_template.render(context, request))
        
    except template.TemplateDoesNotExist:

        html_template = loader.get_template( 'page-404.html' )
        return HttpResponse(html_template.render(context, request))

    except Exception as e:
        print(e)
    
        html_template = loader.get_template( 'page-500.html' )
        return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
@user_passes_test(lambda u: u.groups.filter(name='tournament_organizer').exists(),
login_url="/login/", redirect_field_name='next')
def sync_tournament_data(request):
    context = getContext(request)
    if not checkLoginIsValid(context['gbo_user']):
        return redirect('login')

    helper.update_user_tournament_events(context['gbo_user'], context['tourn'])
    #update_user_tournament_events_async.delay(model_to_dict(context['gbo_user']), model_to_dict(context['tourn']))
    context['segment'] = 'index'
    context['segment_title'] = 'Overview'

    html_template = loader.get_template( 'index.html' )
    return HttpResponse(html_template.render(context, request))

def create_teamtestdata(request, pk_tevent):
    context = getContext(request)
    if not checkLoginIsValid(context['gbo_user']):
        return redirect('login')

    #helper.create_teams_testdata(pk_tevent)

    #tstate = TournamentState.objects.get(id=31)
    #helper.calculate_tstate()
    #helper.create_global_pstats(94)
    #helper.create_global_pstats(95)
    create_game_report.import_game_report_excel()

    helper.recalc_global_pstats(94)
    helper.recalc_global_pstats(95)

    #create_game_report.import_game_report_excel()

    context['segment'] = 'index'
    context['segment_title'] = 'Overview'

    html_template = loader.get_template( 'index.html' )
    return HttpResponse(html_template.render(context, request))

def running_game(request, pk_tourn, courtid):
    #context = getContext(request)
    #if not checkLoginIsValid(context['gbo_user']):
    #    return redirect('login')
    context = {}
    games = Game.objects.select_related("team_st_a__team", "team_st_b__team").filter(tournament=pk_tourn,
                                                                                        court=courtid,
                                                                                        gamestate='RUNNING').first()
    context['game'] = games
    html_template = loader.get_template( 'beachhandball/running_game.html' )
    return HttpResponse(html_template.render(context, request))

