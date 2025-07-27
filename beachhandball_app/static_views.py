# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import re

from django.urls import reverse
# from beachhandball_app.tasks import update_user_tournament_events_async
from datetime import datetime, timedelta
import time
import json
from django.contrib.auth.models import User, Group
from django.db.models.query import Prefetch
from django.forms.models import model_to_dict
from rest_framework.renderers import JSONRenderer
from django.utils.dateparse import parse_datetime
from django.contrib import messages
from django.contrib.messages import get_messages

from django.views.generic import TemplateView
from beachhandball_app import helper, wizard
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django import template
from django.db.models import Q
from django.middleware.csrf import get_token

from authentication.models import GBOUser, ScoreBoardUser
from .models.Tournaments import Court, Referee, Tournament, TournamentEvent, TournamentSettings, TournamentStage, TournamentState
from .models.Team import Team, TeamStats
from .models.Series import Season
from .models.Game import Game
from beachhandball_app.forms.basic_setup.forms import CourtForm, TournamentSettingsForm, RefereeForm
from beachhandball_app.api.serializers.game import GameSerializer,GameRunningSerializer, serialize_game
from beachhandball_app.game_report import helper_game_report
from .services.services import SWS

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
@user_passes_test(lambda u: u.groups.filter(name='tournament_organizer').exists(),
login_url="/login/", redirect_field_name='next')
def tournament_setup(request):
    context = {}

    guser = GBOUser.objects.filter(user=request.user).first()

    #seasons = Season.objects.filter(is_actual=True)
    
    if guser is None:
        return redirect('login')
    else:
        context['gbo_user'] = guser
        #context['season_active'] = seasons# guser.season_active['name'] #SWS.getSeasonActive(guser)
        context['token'] = guser.token

    if not helper.checkLoginIsValid(context['gbo_user']):
        return redirect('login')

    # Handle POST: set selected tournament and redirect
    if request.method == 'POST':
        selected_ids = request.POST.getlist('tournament_ids')
        all_tourns = Tournament.objects.filter(organizer_orm=guser)
        all_tourns.update(is_active=False)
        if selected_ids:
            
            guser.tournament = all_tourns.filter(id__in=selected_ids).first()
            guser.save()
            all_tourns.filter(id__in=selected_ids).update(is_active=True)
            for tourn in all_tourns.filter(id__in=selected_ids):
                tourn.tournamentevent_set.update(tournament_shared=guser.tournament)
            #     helper.update_user_tournament_events(guser, tourn, guser.gbo_data_all)
            return redirect('/')
        else:
            return redirect('tournament_setup')

    # Get all actual seasons
    seasons = Season.objects.filter(is_actual=True).order_by('-start_ts')
    season_tournaments = []
    for season in seasons:
        tournaments = Tournament.objects.filter(
        organizer_orm=guser,
        season=season
            ).prefetch_related(
                Prefetch(
                    'tournamentevent_set',
                    queryset=TournamentEvent.objects.select_related('category'),
                    to_attr='parental_events'
                ),
                Prefetch(
                    'related_events',
                    queryset=TournamentEvent.objects.select_related('category'),
                    to_attr='related_events_list'
                )
            )
        season_tournaments.append({
            'season': season,
            'tournaments': tournaments
        })

    context['season_tournaments'] = season_tournaments

    
    context['segment'] = 'tournament_setup'
    context['segment_title'] = 'Tournament Setup'

    context['setup_mode'] = 'true'
    context['csrf_token'] = get_token(request)

    html_template = loader.get_template( 'beachhandball/tournament_setup.html' )
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def UpdateGameFromListFunc(request):
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
class UpdateGameFromListAfterDrag(TemplateView):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(UpdateGameFromListAfterDrag, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = {'game': 'Hello World'}
        return JsonResponse(context)
        #return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        game = request.POST['game']
        new_dt = request.POST['datetime']
        game_counter = int(request.POST['game_counter'])
        court_id = int(request.POST['court_id'])
        dt = parse_datetime(new_dt)
        game_obj = Game.objects.filter(pk=game).update(starttime=dt, id_counter=game_counter, court_id=court_id)
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
        context = {'game':game, 'court': court.name, 'court_id': court.id }
        return JsonResponse(context)

def not_in_student_group(user):
    if user:
        return user.groups.filter(name='tournament_organizer').count() == 0
    return False

@login_required(login_url="/login/")
@user_passes_test(lambda u: u.groups.filter(name='tournament_organizer').exists(),
login_url="/login/", redirect_field_name='next')
def index(request):
    context = helper.getContext(request)
    if not helper.checkLoginIsValid(context['gbo_user']):
        return redirect('login')
    
    context['segment'] = 'index'
    context['segment_title'] = 'Overview'

    html_template = loader.get_template( 'index.html' )
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
@user_passes_test(lambda u: u.groups.filter(name='tournament_organizer').exists(), login_url="/login/", redirect_field_name='next')
@require_POST
def delete_all_events(request):
    context = helper.getContext(request)
    if not helper.checkLoginIsValid(context['gbo_user']):
        return redirect('login')

    # Get all events for the user's active tournaments
    tournaments = context.get('tournaments')
    if tournaments:
        for tourn in tournaments:
            # Delete related objects if needed
            TournamentState.objects.filter(tournament_event__tournament=tourn).delete()
            TournamentStage.objects.filter(tournament_event__tournament=tourn).delete()
            Game.objects.filter(tournament_event__tournament=tourn).delete()
            TournamentEvent.objects.filter(tournament=tourn).delete()

    messages.success(request, "All events have been deleted.")
    return redirect('index')

@login_required(login_url="/login/")
@user_passes_test(lambda u: u.groups.filter(name='tournament_organizer').exists(), 
                  login_url="/login/", redirect_field_name='next')
def update_games_tournament_shared(request):
    """
    Check all games belonging to the user's tournaments and ensure the tournament_shared field is properly set.
    If tournament_shared is not set or is different from the user's active tournament, update it.
    """
    context = helper.getContext(request)
    if not helper.checkLoginIsValid(context['gbo_user']):
        return redirect('login')
    
    guser = context['gbo_user']
    active_tournament = guser.tournament
    
    if not active_tournament:
        messages.error(request, "No active tournament selected.")
        return redirect('index')
    
    updated_count = 0
    
    # Get all games for all user's tournaments
    for tournament in context.get('tournaments', []):
        # Get games associated with this tournament
        games = Game.objects.filter(tournament=tournament)
        
        # Print debug info
        print(f"Tournament {tournament.id} - {tournament.name}")
        print(f"Found {games.count()} games")
        
        # Check if any game has tournament_shared == None
        null_shared_count = games.filter(tournament_shared__isnull=True).count()
        print(f"Games with NULL tournament_shared: {null_shared_count}")
        
        # Check if any game has wrong tournament_shared
        wrong_shared_count = games.exclude(tournament_shared=active_tournament).count()
        print(f"Games with wrong tournament_shared: {wrong_shared_count}")
        
        # Update games where tournament_shared is not set or different
        games_to_update = games.filter(
            Q(tournament_shared__isnull=True) | 
            ~Q(tournament_shared=active_tournament)
        )
        
        if games_to_update.exists():
            count_before_update = games_to_update.count()
            print(f"Updating {count_before_update} games")
            
            # Update each game with proper tournament_shared
            for game in games_to_update:
                print(f"Game {game.id}: tournament_shared was {game.tournament_shared_id}, setting to {active_tournament.id}")
                game.tournament_shared = active_tournament
                game.save()
            
            updated_count += count_before_update
    
    if updated_count > 0:
        messages.success(request, f"Updated tournament_shared field for {updated_count} games.")
    else:
        messages.info(request, "All games already have the correct tournament_shared field.")
    
    # Redirect back to the referring page or to index
    return_url = request.META.get('HTTP_REFERER', reverse('index'))
    return redirect(return_url)

@login_required(login_url="/login/")
@user_passes_test(lambda u: u.groups.filter(name='tournament_organizer').exists(), 
                  login_url="/login/", redirect_field_name='next')
def update_games_tournament_id(request):
    context = helper.getContext(request)
    if not helper.checkLoginIsValid(context['gbo_user']):
        return redirect('login')
    
    guser = context['gbo_user']
    active_tournament = guser.tournament
    
    if not active_tournament:
        messages.error(request, "No active tournament selected.")
        return redirect('index')
    
    updated_count = 0
    
    # Get all games for all user's tournaments
    for tournament in context.get('tournaments', []):
        # Get games associated with this tournament
        games = Game.objects.filter(tournament=tournament)
        
        # Print debug info
        print(f"Tournament {tournament.id} - {tournament.name}")
        print(f"Found {games.count()} games")

            # Update each game with proper tournament_shared
        for game in games.all():
            if game.tournament != game.tournament_event.tournament:
                game.tournament = game.tournament_event.tournament
                game.save()
    
    messages.info(request, "All games already have the correct tournament_shared field.")
    
    # Redirect back to the referring page or to index
    return_url = request.META.get('HTTP_REFERER', reverse('index'))
    return redirect(return_url)

@login_required(login_url="/login/")
@user_passes_test(lambda u: u.groups.filter(name='tournament_organizer').exists(),
login_url="/login/", redirect_field_name='next')
def setup_wizard(request, pk_tevent):
    context = helper.getContext(request)
    if not helper.checkLoginIsValid(context['gbo_user']):
        return redirect('login')
    for te in context['events']:
        if te.id == pk_tevent:
            context['tevent'] = te
            break
    context['segment'] = 'index'
    context['segment_title'] = 'Overview'

    # if request.method == 'POST':
    #     structure_data = json.loads(request.POST['structure-data'])
    #     result = wizard.wizard_create_structure(te, structure_data)
    #     return HttpResponseRedirect(reverse("structure_setup.detail", kwargs={"pk": pk_tevent}))

    if request.method == 'POST':
        structure_data = json.loads(request.POST['structure-data'])
        result = wizard.wizard_create_structure(te, structure_data)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'redirect_url': reverse("structure_setup.detail", kwargs={"pk": pk_tevent})})
        return HttpResponseRedirect(reverse("structure_setup.detail", kwargs={"pk": pk_tevent}))

    html_template = loader.get_template( 'forms-setup-wizard.html' )
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

@login_required(login_url="/login/")
@user_passes_test(lambda u: u.groups.filter(name='tournament_organizer').exists(),
login_url="/login/", redirect_field_name='next')
def setup_wizard_gameplan(request):
    context = helper.getContext(request)
    if not helper.checkLoginIsValid(context['gbo_user']):
        return redirect('login')

    context['segment'] = 'game_plan'
    context['segment_title'] = 'Game Plan'
    context['game_plan_url'] = reverse("game_plan")
    context['tournament_data'] = ''
    context['tournament_settings'] = TournamentSettings.objects.get(tournament=context['tourn'])
    context['num_courts'] = Court.objects.filter(tournament=context['tourn'] ).count()
    if context['num_courts'] == 0:
        context['num_courts'] = 1

    if request.method == 'POST':
        context['tournament_settings'].game_slot_mins = int(request.POST['gameplan-data-minutes-per-game'])
        context['tournament_settings'].first_game_slot = helper.parse_time_from_picker(request.POST['gameplan-data-datetime-firstgame'])
        gameplan_data_all_games = json.loads(request.POST['gameplan-data-all-games'])
        context['tournament_settings'].game_counter = wizard.wizard_create_gameplan(context['tourn'], gameplan_data_all_games, request.POST['gameplan-data-num-courts'])
        context['tournament_settings'].game_slot_counter = context['tournament_settings'].game_counter
        context['tournament_settings'].save()
        return HttpResponseRedirect(reverse("game_plan"))

    context['tournament_data'] = json.dumps(helper.get_tournament_multi_info_json(context['tournaments']), default=str, separators=(',', ':'), indent=None)

    html_template = loader.get_template( 'forms-setup-wizard-gameplan.html' )
    return HttpResponse(html_template.render(context, request))



@login_required(login_url="/login/")
@user_passes_test(lambda u: u.groups.filter(name='tournament_organizer').exists(),
login_url="/login/", redirect_field_name='structure_setup')
def delete_gameplan(request):
    context = helper.getContext(request)
    if not helper.checkLoginIsValid(context['gbo_user']):
        return redirect('login')

    context['segment'] = 'structure_setup'
    context['segment_title'] = 'Structure Setup'

    if request.method == 'POST':
        print('Delete all games')
        Game.objects.filter(tournament=context['tourn']).delete()
        return HttpResponseRedirect(reverse("game_plan"))
    elif request.method == 'GET':
        html_template = loader.get_template( 'beachhandball/delete_gameplan_confirmation.html' )
        return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
@user_passes_test(lambda u: u.groups.filter(name='tournament_organizer').exists(),
login_url="/login/", redirect_field_name='next')
def basic_setup(request):
    
    context = helper.getContext(request)
    if not helper.checkLoginIsValid(context['gbo_user']):
        return redirect('login')
    context['form_refs'] = RefereeForm(initial={'referees_list': 'Enter referees: name, first_name'})
    formCourt = None
    context['form_sender'] = ''

    if request.method == 'POST' and request.POST.get('form_sender') == 'referee_create':
        context['form_sender'] = 'referee_create'
        form = RefereeForm(request.POST)
        if form.is_valid():
            referees_list = form.cleaned_data['referees_list']
            referees_data = referees_list.strip().split('\n')

            for referee_data in referees_data:
                try:
                    name, first_name, abbreviation = re.split(r'[,:;]', referee_data.strip())
                    if is_valid_data(name.strip(), first_name.strip(), abbreviation.strip()):
                        print(name + ' ' + first_name + ' ' + abbreviation)
                        Referee.objects.get_or_create(tournament=context['tourn'], name=name.strip(), first_name=first_name.strip(), abbreviation=abbreviation.strip(), gbo_subject_id=0)
                    else:
                        print("Error: Invalid data. Each name, first name, and abbreviation should contain only alphabetic characters.")
                    
                except ValueError:
                    print("Error: Invalid input format. Each line should have 'name,first_name,abbreviation'")
                except Exception as e:
                    print("An error occurred:", e)
            
            context['form_sender'] = ''
            #return redirect('success_page')  # Replace 'success_page' with the URL name of your success page

    if request.method == 'POST' and request.POST.get('form_sender') == 'tourn_settings':
        context['form_sender'] = 'tourn_settings'
        formCourt = CourtForm(tourn_id=context['tourn'].id)
        form = TournamentSettingsForm(request.POST, instance=context['tourn_settings'])
        if form.is_valid():
            form.save()
    
    if request.method == 'POST' and request.POST.get('form_sender') == 'court_create':
        context['form_sender'] = 'court_create'
        form = TournamentSettingsForm(instance=context['tourn_settings'])
        formCourt = CourtForm(request.POST)
        formCourt.tournament = context['tourn']
        if formCourt.is_valid():
            formCourt.save()
            court = formCourt.instance
            court.tournament = context['tourn']
            court.save()
            #create scoreboard user
            username = str(context['tourn'].id) + '_' + court.name.replace(" ", "_")
            user = User.objects.create_user(username, 'c@c.c', username)
            user.first_name = str(court.number)
            user.last_name = court.name
            user.save()
            #check if user is TO
            sb_group, cr = Group.objects.get_or_create(name='scoreboard')
            # add permissions to to_group
            sb_group.user_set.add(user)
            sb_group.save()
            
            sbUser = ScoreBoardUser(user=user, court=court)
            sbUser.save()
            
    
    #if request.method == 'GET':
    form = TournamentSettingsForm(instance=context['tourn_settings'])
    if formCourt is None:
        formCourt = CourtForm(tourn_id=context['tourn'].id)

    context['segment'] = 'basic_setup'
    context['segment_title'] = 'Basic Setup'

    context['tourn_settings_form'] = form
    context['court_form'] = formCourt
    context['courts'] = context['tourn'].court_set.all()
    context['scoreboard_users'] = ScoreBoardUser.objects.filter(court__tournament=context['tourn']).all()

    html_template = loader.get_template( 'beachhandball/basic_setup.html' )
    return HttpResponse(html_template.render(context, request))

def is_valid_data(name, first_name, abbreviation):
    return name.isalpha() and first_name.isalpha() and abbreviation.isalpha()

@login_required(login_url="/login/")
@user_passes_test(lambda u: u.groups.filter(name='tournament_organizer').exists(),
login_url="/login/", redirect_field_name='next')
def basic_setup_delete_referee(request, pk_tourn, referee_id):
    try:
        referee = Referee.objects.get(pk=referee_id)
        referee.delete()
    except Referee.DoesNotExist:
        pass  # Optionally handle the case where the referee with the given ID does not exist

    return redirect('basic_setup')

@login_required(login_url="/login/")
@user_passes_test(lambda u: u.groups.filter(name='tournament_organizer').exists(),
login_url="/login/", redirect_field_name='next')
def teams_setup(request):
    
    context = helper.getContext(request)
    if not helper.checkLoginIsValid(context['gbo_user']):
        return redirect('login')

    context['segment'] = 'teams_setup'
    context['segment_title'] = 'Teams Setup'

    html_template = loader.get_template( 'beachhandball/teams_setup.html' )
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
@user_passes_test(lambda u: u.groups.filter(name='tournament_organizer').exists(),
login_url="/login/", redirect_field_name='next')
def structure_setup(request):
    
    context = helper.getContext(request)
    if not helper.checkLoginIsValid(context['gbo_user']):
        return redirect('login')

    context['segment'] = 'structure_setup'
    context['segment_title'] = 'Structure Setup'

    html_template = loader.get_template( 'beachhandball/structure_setup.html' )
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
@user_passes_test(lambda u: u.groups.filter(name='tournament_organizer').exists(),
login_url="/login/", redirect_field_name='next')
def game_plan(request):
    
    context = helper.getContext(request)
    if not helper.checkLoginIsValid(context['gbo_user']):
        return redirect('login')

    tourn = context['tourn']
    tournaments = context.get('tournaments', [])
    if not tournaments:
        messages.warning(request, "No tournaments available.")
        return redirect('index')
    tevents = context['events']
    orderbyList  = ['starttime','court__name']

    all_games = []
    all_courts = []
    all_refs = []
    all_states = []

    #games = Game.objects.filter(tournament=tevent.tournament).all().order_by(*orderbyList)
    # tourn_data = Tournament.objects.prefetch_related(
    #         Prefetch("game_set", queryset=Game.objects.select_related("tournament", "tournament_event__category", "team_a", "team_b", "team_st_a__team", "team_st_b__team", "ref_a", "ref_b", "tournament_state__tournament_stage", "court").order_by(*orderbyList)
    #             , to_attr="all_games"),
    #         Prefetch("tournamentevent_set", queryset=TournamentEvent.objects.select_related("tournament", "category").prefetch_related(
    #             Prefetch("tournamentstate_set", queryset=TournamentState.objects.select_related("tournament_event__category", "tournament_stage")
    #             , to_attr="all_tstates")
    #         )
    #             , to_attr="all_tevents"),
    #         Prefetch("court_set", queryset=Court.objects.select_related("tournament")
    #             , to_attr="all_courts"),
    #         Prefetch("referee_set", queryset=Referee.objects.select_related("tournament")
    #             , to_attr="all_refs")
    #             ).get(id=tourn.id)
    #all_tstates_qs = Q()
    #for event in tevents:
    #    all_tstates_qs = all_tstates_qs | Q(tournament_event=event, is_final=False)
    

    # Get data for each tournament
    for tournament in tournaments:
        try:
            tourn_data = Tournament.objects.prefetch_related(
                Prefetch(
                    "game_set", 
                    queryset=Game.objects.select_related(
                        "tournament", 
                        "tournament_event__category", 
                        "team_a", 
                        "team_b", 
                        "team_st_a__team", 
                        "team_st_b__team", 
                        "ref_a", 
                        "ref_b", 
                        "tournament_state__tournament_stage", 
                        "court"
                    ).order_by(*orderbyList),
                    to_attr="all_games"
                ),
                Prefetch(
                    "tournamentevent_set", 
                    queryset=TournamentEvent.objects.select_related("tournament", "category").prefetch_related(
                        Prefetch(
                            "tournamentstate_set", 
                            queryset=TournamentState.objects.select_related("tournament_event__category", "tournament_stage"),
                            to_attr="all_tstates"
                        )
                    ),
                    to_attr="all_tevents"
                ),
                Prefetch(
                    "court_set", 
                    queryset=Court.objects.select_related("tournament"),
                    to_attr="all_courts"
                ),
                Prefetch(
                    "referee_set", 
                    queryset=Referee.objects.select_related("tournament"),
                    to_attr="all_refs"
                )
            ).get(id=tournament.id)
            
            # Collect games
            all_games.extend(tourn_data.all_games)
            
            # Collect courts
            all_courts.extend(tourn_data.all_courts)
            
            # Collect referees
            all_refs.extend(tourn_data.all_refs)
            
            # Collect tournament states that are not final
            for te in tourn_data.all_tevents:
                for ts in te.all_tstates:
                    if ts.is_final is False:
                        all_states.append(ts)
                        
        except Tournament.DoesNotExist:
            print(f"Tournament with ID {tournament.id} not found")
            continue
        
    tstates = []
    for te in tourn_data.all_tevents:
        #print(te.category)
        for ts in te.all_tstates:
            #print(ts.tournament_event.category)
            if ts.is_final is False:
                tstates.append(ts)
    # Sort all items by appropriate fields
    all_games.sort(key=lambda x: (x.starttime, x.court.name if x.court else ""))
    all_courts.sort(key=lambda x: x.name)
    all_refs.sort(key=lambda x: x.name)

    context['tstates'] = all_states #TournamentState.objects.filter(all_tstates_qs)
    context['segment'] = 'game_plan'
    context['segment_title'] = 'Game Plan'

    context['courts'] = list(Court.objects.filter(tournament=tourn).select_related("tournament"))
     #Court.objects.filter(tournament=tourn)
    context['referees'] = all_refs #Referee.objects.filter(tournament=tourn)

    #data_list = str(JSONRenderer().render(GameSerializer(tourn.game_set.all(), many=True).data), 'utf-8')
    context['games'] = all_games
    #for g in tourn_data.all_games:
    #    print(str(g.tournament_event.category))
    #JSONRenderer().render(GameRunningSerializer(tourn.game_set.all(), many=True).data)

    html_template = loader.get_template( 'beachhandball/game_plan.html' )
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
@user_passes_test(lambda u: u.groups.filter(name='tournament_organizer').exists(),
login_url="/login/", redirect_field_name='next')
def game_plan_v3(request):
    context = helper.getContext(request)
    if not helper.checkLoginIsValid(context['gbo_user']):
        return redirect('login')

    tourn = context['tourn']
    tevents = context['events']

    # Example data
    courts = [{"id": 1, "name": "Court 1"}, {"id": 2, "name": "Court 2"}]
    games = [
        {"id": 1, "team_a": "Team A1", "team_b": "Team B1", "court": {"id": 1}, "starttime": "09:00"},
        {"id": 2, "team_a": "Team A2", "team_b": "Team B2", "court": {"id": 2}, "starttime": "09:45"},
    ]

    # Generate time slots (e.g., 09:00 to 18:00 in 45-minute intervals)
    start_time = datetime.strptime("09:00", "%H:%M")
    end_time = datetime.strptime("18:00", "%H:%M")
    time_slots = []
    while start_time <= end_time:
        time_slots.append(start_time.strftime("%H:%M"))
        start_time += timedelta(minutes=45)

    return render(request, "beachhandball/game_plan_v3.html", {
        "courts": courts,
        "games": games,
        "time_slots": time_slots,
        "tourn": context['tourn'],
    })

@login_required(login_url="/login/")
@user_passes_test(lambda u: u.groups.filter(name='tournament_organizer').exists(),
login_url="/login/", redirect_field_name='next')
def results(request):
    
    context = helper.getContext(request)
    if not helper.checkLoginIsValid(context['gbo_user']):
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
    context = helper.getContext(request)
    if not helper.checkLoginIsValid(context['gbo_user']):
        return redirect('login')

    context['gbo_user'].gbo_data_all, execution_time = SWS.syncTournamentData(context['gbo_user'], context['tourn'].season.gbo_season_id)
    helper.update_user_tournament_events(context['gbo_user'], context['tourn'])
    
    
    #update_user_tournament_events_async.delay(model_to_dict(context['gbo_user']), model_to_dict(context['tourn']))
    context['segment'] = 'index'
    context['segment_title'] = 'Overview'

    html_template = loader.get_template( 'index.html' )
    return HttpResponse(html_template.render(context, request))

def create_teamtestdata(request, pk_tevent):
    context = helper.getContext(request)
    if not helper.checkLoginIsValid(context['gbo_user']):
        return redirect('login')

    #helper.create_teams_testdata(pk_tevent)

    #tstate = TournamentState.objects.get(id=31)
    #helper.calculate_tstate()
    #helper.create_global_pstats(94)
    #helper.create_global_pstats(95)
    helper_game_report.create_pregame_report_excel.import_game_report_excel()

    helper.recalc_global_pstats(94)
    helper.recalc_global_pstats(95)

    #create_game_report.import_game_report_excel()

    context['segment'] = 'index'
    context['segment_title'] = 'Overview'

    html_template = loader.get_template( 'index.html' )
    return HttpResponse(html_template.render(context, request))

def running_game(request, pk_tourn, courtid):
    #context = helper.getContext(request)
    #if not helper.checkLoginIsValid(context['gbo_user']):
    #    return redirect('login')
    context = {}
    games = Game.objects.select_related("team_st_a__team", "team_st_b__team").filter(tournament=pk_tourn,
                                                                                        court=courtid,
                                                                                        gamestate='RUNNING').first()
    context['game'] = games
    html_template = loader.get_template( 'beachhandball/running_game.html' )
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
@user_passes_test(lambda u: u.groups.filter(name='tournament_organizer').exists(),
login_url="/login/", redirect_field_name='next')
def recalc_global_stats(request, pk_tevent):
    context = helper.getContext(request)
    if not helper.checkLoginIsValid(context['gbo_user']):
        return redirect('login')
    for te in context['events']:
        if te.id == pk_tevent:
            context['tevent'] = te
            break
    context['segment'] = 'results'
    context['segment_title'] = 'Results'

    if request.method == 'GET':
        helper.recalc_global_pstats(pk_tevent)

    return redirect(reverse('results.detail', kwargs={'pk':pk_tevent}))