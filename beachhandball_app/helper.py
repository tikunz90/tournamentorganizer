import json
import traceback

import unicodedata
import time
from datetime import datetime
from collections import defaultdict

from django.db import transaction
from django.db.models.query import Prefetch
from django.db.models.signals import post_save
from authentication.models import GBOUser, GBOUserSerializer
from beachhandball_app.api.serializers.tournament.serializer import serialize_tournament_full, serialize_tournament_light, serialize_tournament_multi_full
from beachhandball_app.models.Player import Player, PlayerStats
from django.db.models.query_utils import Q, check_rel_lookup_compatibility
from beachhandball_app import signals
from beachhandball_app.models.choices import GAMESTATE_CHOICES, TOURNAMENT_STAGE_TYPE_CHOICES
from beachhandball_app.models.Tournaments import Court, Referee, Tournament, TournamentEvent, TournamentSettings, TournamentStage, TournamentState, TournamentTeamTransition
from beachhandball_app.models.Game import Game
from beachhandball_app.models.Team import Coach, TeamStats, Team
from beachhandball_app.models.General import TournamentCategory
from beachhandball_app.models.Series import Season
from django.utils.http import urlencode
from django.urls import reverse
from django.utils.dateparse import parse_datetime

from beachhandball_app.services.services import SWS

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
    
    # Get all active tournaments for this user in the current season
    tournaments = Tournament.objects.prefetch_related(
        Prefetch(
            "tournamentsettings_set",
            queryset=TournamentSettings.objects.all(),
            to_attr="settings"
        ),
        Prefetch(
            "tournamentevent_set",
            queryset=TournamentEvent.objects.select_related("category").all(),
            to_attr="events"
        )
    ).filter(
        organizer_orm=guser,
        is_active=True,
        season__is_actual=True
    )

    context['tournaments'] = tournaments  # <-- Pass tournaments to context

    t = next((t for t in tournaments if t.id == guser.tournament_id), None)
    context['tourn'] = guser.tournament
    context['tourn_settings'] = t.settings[0] if t and t.settings else None
    # Collect all events from all active tournaments
    all_events = []
    for tourn in tournaments:
        all_events.extend(getattr(tourn, 'events', []))
    context['events'] = all_events
    print('Exit getContext', datetime.now())
    return context

def checkLoginIsValid(gbouser):
    if not gbouser.is_online:
        return True
    if int(time.time()) > time.mktime(gbouser.validUntil.timetuple()):
        return False
    else:
        return True

def update_active_seasons(active_seasons):
    #get existing seasons
    seasons = Season.objects.all()
    season_list = [s for s in seasons]

    # Build a set of GBO season IDs from the incoming JSON
    json_season_ids = set()
    now_ts = int(time.time())  # current time in seconds

    for gbo_season in active_seasons:
        json_season_ids.add(gbo_season['id'])
        django_season = next((x for x in season_list if x.gbo_season_id==gbo_season['id']), None)
        end_at_ts = int(gbo_season.get('end_at_ts', '0')) // 1000  # convert ms to s

        if django_season is None:
            django_season, cr = Season.objects.get_or_create(name=gbo_season['name'], gbo_season_id=gbo_season['id'], is_actual=True)
        else:
            season_list = [ x for x in season_list if x is not django_season ]
        # Set is_active based on end_at_ts
        if end_at_ts and end_at_ts < now_ts:
            django_season.is_actual = False
        else:
            django_season.is_actual = True
        django_season.save()

    # Any remaining Django seasons not in the JSON should be set to inactive
    for s in season_list:
        if s.gbo_season_id not in json_season_ids:
            s.is_actual = False
            s.save()

def update_user_with_gbo(gbouser):
    seasons = Season.objects.filter(is_actual=True)
    gbo_data = {}
    gbo_gc_data = {}
    for season in seasons:
        data, execution_time = SWS.syncTournamentData(gbouser, season.gbo_season_id)
        datagc, execution_time = SWS.syncTournamentGCData(gbouser, season.gbo_season_id)
        gbo_data[season.gbo_season_id] = data.get('message', [])
        gbo_gc_data[season.gbo_season_id] = datagc.get('message', [])
    gbouser.gbo_data_all = gbo_data
    gbouser.gbo_gc_data = gbo_gc_data

def update_user_tournament(gbouser, seasons):
    begin = time.time()
    print("ENTER update_user_tournament")

    #season = Season.objects.filter(gbo_season_id=season_id).first()

    print("season_cup_tournament...")
    # tourns_q = Tournament.objects.prefetch_related(
    #     Prefetch("tournamentsettings_set", queryset=TournamentSettings.objects.all(), to_attr="settings")).filter(organizer=gbouser.subject_id, season__gbo_season_id=season_id)
    tourns_q = Tournament.objects.prefetch_related(
        Prefetch("tournamentsettings_set", queryset=TournamentSettings.objects.all(), to_attr="settings")).filter(organizer_orm=gbouser)
    tourns = [t for t in tourns_q]
    tourns_cup = [t for t in tourns if t.season_cup_tournament_id != 0]
    tourns_subcup = [t for t in tourns if t.sub_season_cup_tournament_id != 0]
    tourns_dm = [t for t in tourns if t.season_cup_german_championship_id != 0]

    #gbo_data = gbouser.gbo_data
    gbo_data = gbouser.gbo_data_all

    for season_id ,gbot in gbo_data.items():
        tourn_found = False
        if isinstance(gbot, list) and len(gbot) > 0:
            gbot = gbot[0]
        else:
            continue  # or handle the empty case as needed
        season = Season.objects.filter(gbo_season_id=season_id).first()
        if not season:
            continue
        season_tourn = gbot['seasonTournament']
        season_tourn_subject_id = season_tourn['seasonSubject']['subject']['id']
        if season_tourn_subject_id != gbouser.subject_id:
            continue
        gbo_tourn = season_tourn['tournament']

        to_tourn = None

        tourns_by_season_cup_id = [t for t in tourns if t.season_cup_tournament_id == gbot['id']]

        # Find existing Tournament object and update
        for t in tourns_cup:
            if t.season_tournament_id == season_tourn['id']:
                print("Found season_tourn")
                to_tourn = t
                tourn_found = True
                t.organizer=gbouser.subject_id
                t.organizer_orm = gbouser
                t.name=gbo_tourn['name']
                t.last_sync_at=datetime.now()
                t.season_tournament_id=season_tourn['id']
                t.season_cup_tournament_id=gbot['id']
                t.season = season
                t.save()
                ts, cr = TournamentSettings.objects.get_or_create(tournament=t)
                ts.save()
                update_user_tournament_events(gbouser, t, gbot)
                sync_referees_of_tournament(gbo_data, t)
        if not tourn_found and len(tourns_by_season_cup_id) == 0:
            #create tournament
            new_t = Tournament(organizer=gbouser.subject_id,
            organizer_orm=gbouser,
            name=gbo_tourn['name'],
            last_sync_at=datetime.now(),
            season_tournament_id=season_tourn['id'],
            season_cup_tournament_id=gbot['id'],
            season=season)
            new_t.save()
            ts, cr = TournamentSettings.objects.get_or_create(tournament=new_t)
            ts.save()
            update_user_tournament_events(gbouser, new_t)
            to_tourn = new_t
            tourns.append(new_t)
        else:
            print("Tournament exists but is assigned to other user")
        
    end = time.time()
    execution_time = end - begin
    # return tourns, execution_time

    print("season_cup_german_championship")
    gbo_data = gbouser.gbo_gc_data
    for season_id, gbot in gbo_data.items():
        tourn_found = False
        
        if isinstance(gbot, list) and len(gbot) > 0:
            gbot = gbot[0]
        else:
            continue  # or handle the empty case as needed
        season = Season.objects.filter(gbo_season_id=season_id).first()
        if not season:
            print(f"Season with gbo_season_id {season_id} not found.")
            continue
            
        season_tourn = gbot['seasonTournament']
        gbo_tourn = season_tourn['tournament']

        to_tourn = None
        tourns_by_season_cup_id = Tournament.objects.filter(season_cup_german_championship_id=gbot['id'])
        for t in tourns_dm:
            if t.season_german_championship_id == season_tourn['id']:
                print("Found season_tourn")
                to_tourn = t
                tourn_found = True
                t.organizer=gbouser.subject_id
                t.organizer_orm = gbouser
                t.name=gbo_tourn['name']
                t.last_sync_at=datetime.now()
                t.season_german_championship_id=season_tourn['id']
                t.season_cup_german_championship_id=gbot['id']
                t.season = season
                t.save()
                ts, cr = TournamentSettings.objects.get_or_create(tournament=t)
                ts.save()
                update_user_tournament_events(gbouser, t, gbot)
                sync_referees_of_tournament(gbo_data, t)
        if not tourn_found and tourns_by_season_cup_id.count() == 0:
            #create tournament
            new_t = Tournament(organizer=gbouser.subject_id,
            organizer_orm = gbouser,
            name=gbo_tourn['name'],
            last_sync_at=datetime.now(),
            season_german_championship_id=season_tourn['id'],
            season_cup_german_championship_id=gbot['id'],
            season=season)
            new_t.save()
            ts, cr = TournamentSettings.objects.get_or_create(tournament=new_t)
            ts.save()
            to_tourn = new_t
            tourns_dm.append(new_t)
            update_user_tournament_events(gbouser, new_t, gbot)
            sync_referees_of_tournament(gbo_data, new_t)
        else:
            print("Tournament exists but is assigned to other user")
    print("sub-season")
    end = time.time()
    execution_time = end - begin
    return tourns + tourns_dm, execution_time


    gbo_data = gbouser.gbo_sub_data
    if not gbo_data['isError']:
        gbo_data = gbo_data['message']

        for gbot in gbo_data:
            tourn_found = False
            
            season_tourn = gbot['seasonTournament']
            gbo_tourn = season_tourn['tournament']

            to_tourn = None
            #tourns = Tournament.objects.filter(organizer=gbouser.subject_id)
            tourns = Tournament.objects.filter(organizer_orm=gbouser)
            tourns_by_season_cup_id = Tournament.objects.filter(sub_season_cup_tournament_id=gbot['id'])
            for t in tourns:
                if t.season_tournament_id == gbot['id']:
                    print("Found season_tourn")
                    to_tourn = t
                    tourn_found = True
                    t.organizer=gbouser.subject_id
                    t.organizer_orm = gbouser
                    t.name=gbo_tourn['name']
                    t.last_sync_at=datetime.now()
                    t.season_tournament_id=season_tourn['id']
                    t.sub_season_cup_tournament_id=gbot['id']
                    t.season=season
                    t.save()
                    ts, cr = TournamentSettings.objects.get_or_create(tournament=t)
                    ts.save()
                    update_user_tournament_events(gbouser, t)
            if not tourn_found and tourns_by_season_cup_id.count() == 0:
                #create tournament
                new_t = Tournament(organizer=gbouser.subject_id,
                organizer_orm = gbouser,
                name=gbo_tourn['name'],
                last_sync_at=datetime.now(),
                season_tournament_id=season_tourn['id'],
                sub_season_cup_tournament_id=gbot['id'],
                season=season)
                new_t.save()
                ts, cr = TournamentSettings.objects.get_or_create(tournament=new_t)
                ts.save()
                to_tourn = new_t
                update_user_tournament_events(gbouser, new_t)
            else:
                print("Tournament exists but is assigned to other user")

def update_user_tournament_events(gbouser, tournament_obj, gbo_data):
    begin = time.time()
    print("ENTER update_user_tournament_events", datetime.now())
    try:
        if type(gbouser) is GBOUser:
            gbouser = gbouser.__dict__
        if type(tournament_obj) is Tournament:
            to_tourn = tournament_obj.__dict__
        cup_type = 'is_cup'
        if to_tourn['season_cup_tournament_id'] != 0:
            #gbo_data = gbouser['gbo_data_all']
            cup_type = 'is_cup'
        elif to_tourn['season_cup_german_championship_id'] != 0:
            #gbo_data = gbouser['gbo_gc_data']
            cup_type = 'is_gc'
        elif to_tourn['sub_season_cup_tournament_id'] != 0:
            #gbo_data = gbouser['gbo_sub_data']
            cup_type = 'is_sub'
        else:
            print("No ID to any gbo tournament")
            return
        if True: #not gbo_data['isError']:
            # Prefetch all categories for this tournament
            category_ids = [cat['category']['id'] for cat in gbo_data['seasonTournament']['seasonTournamentCategories']]
            #category_ids = [cat['category']['id'] for gbot in gbo_data for cat in gbot['seasonTournament']['seasonTournamentCategories']]
            existing_cats = TournamentCategory.objects.filter(gbo_category_id__in=category_ids)
            cat_map = {(cat.gbo_category_id, cat.classification, cat.name, cat.category): cat for cat in existing_cats}
            new_cats = []
            new_cat_keys = set()

            # Prefetch all events for this tournament
            event_filter = Q()
            season_tourn = gbo_data['seasonTournament']
            for cat in season_tourn['seasonTournamentCategories']:
                if cup_type == 'is_cup':
                    event_filter |= Q(
                        tournament_id=to_tourn['id'],
                        category__gbo_category_id=cat['category']['id'],
                        season_cup_tournament_id=gbo_data['id']
                    )
                elif cup_type == 'is_gc':
                    event_filter |= Q(
                        tournament_id=to_tourn['id'],
                        category__gbo_category_id=cat['category']['id'],
                        season_cup_german_championship_id=gbo_data['id']
                    )
                elif cup_type == 'is_sub':
                    event_filter |= Q(
                        tournament_id=to_tourn['id'],
                        category__gbo_category_id=cat['category']['id'],
                        sub_season_cup_tournament_id=gbo_data['id']
                    )
            existing_events = TournamentEvent.objects.filter(event_filter)
            event_map = {}
            for ev in existing_events:
                key = (ev.category.gbo_category_id, getattr(ev, 'season_cup_tournament_id', 0), getattr(ev, 'season_cup_german_championship_id', 0), getattr(ev, 'sub_season_cup_tournament_id', 0))
                event_map[key] = ev
            new_events = []


            season_tourn = gbo_data['seasonTournament']
            doNewCategory = True
            if cup_type == 'is_cup' and season_tourn['id'] != to_tourn['season_tournament_id']:
                doNewCategory = False
            elif cup_type == 'is_gc' and season_tourn['id'] != to_tourn['season_german_championship_id']:
                doNewCategory = False
            elif cup_type == 'is_sub':
                doNewCategory = False
            if doNewCategory:
                # read dates
                if not season_tourn['seasonTournamentWeeks']:
                    print("Not weeks defined")
                start_ts = int(season_tourn['seasonTournamentWeeks'][0]['seasonWeek']['start_at_ts'])/1000
                end_ts = int(season_tourn['seasonTournamentWeeks'][0]['seasonWeek']['end_at_ts'])/1000

                for cat in season_tourn['seasonTournamentCategories']:
                    abbrv = 'M' if cat['category']['gender']['name'] == 'man' else 'W'
                    cat_key = (cat['category']['id'], cat['category']['name'], cat['category']['gender']['name'], cat['category']['gender']['name'])
                    tcat = cat_map.get(cat_key)
                    if not tcat and cat_key not in new_cat_keys:
                        tcat = TournamentCategory(
                            gbo_category_id=cat['category']['id'],
                            classification=cat['category']['name'],
                            name=cat['category']['gender']['name'],
                            category=cat['category']['gender']['name'],
                            abbreviation=abbrv,
                            season_tournament_category_id=cat['id']
                        )
                        new_cats.append(tcat)
                        new_cat_keys.add(cat_key)
                        cat_map[cat_key] = tcat  # Add to map for later use

            # Bulk create new categories
            if new_cats:
                TournamentCategory.objects.bulk_create(new_cats)
                # Refresh cat_map with DB objects
                created_cats = TournamentCategory.objects.filter(gbo_category_id__in=[c.gbo_category_id for c in new_cats])
                for c in created_cats:
                    cat_key = (c.gbo_category_id, c.classification, c.name, c.category)
                    cat_map[cat_key] = c

            # Now process events
            season_tourn = gbo_data['seasonTournament']
            doNewEvents = True
            if cup_type == 'is_cup' and season_tourn['id'] != to_tourn['season_tournament_id']:
                doNewEvents = False
            elif cup_type == 'is_gc' and season_tourn['id'] != to_tourn['season_german_championship_id']:
                doNewEvents = False
            elif cup_type == 'is_sub':
                doNewEvents = False
            if doNewEvents:
                start_ts = int(season_tourn['seasonTournamentWeeks'][0]['seasonWeek']['start_at_ts'])/1000
                end_ts = int(season_tourn['seasonTournamentWeeks'][0]['seasonWeek']['end_at_ts'])/1000

                for cat in season_tourn['seasonTournamentCategories']:
                    cat_key = (cat['category']['id'], cat['category']['name'], cat['category']['gender']['name'], cat['category']['gender']['name'])
                    tcat = cat_map[cat_key]
                    if cup_type == 'is_cup':
                        event_key = (tcat.gbo_category_id, gbo_data['id'], 0, 0)
                        tevents = [event_map.get(event_key)]
                    elif cup_type == 'is_gc':
                        event_key = (tcat.gbo_category_id, 0, gbo_data['id'], 0)
                        tevents = [event_map.get(event_key)]
                    elif cup_type == 'is_sub':
                        event_key = (tcat.gbo_category_id, 0, 0, gbo_data['id'])
                        tevents = [event_map.get(event_key)]
                    else:
                        tevents = [None]
                    te = None
                    if not tevents[0]:
                        if cup_type == 'is_cup':
                            te = TournamentEvent(
                                tournament=tournament_obj,
                                tournament_shared=tournament_obj,
                                season_tournament_category_id=cat['id'],
                                season_cup_tournament_id=gbo_data['id'],
                                season_tournament_id=season_tourn['id'],
                                name=to_tourn['name'],
                                category=tcat,
                                start_ts=datetime.fromtimestamp(start_ts),
                                end_ts=datetime.fromtimestamp(end_ts),
                                max_number_teams=16,
                                last_sync_at=datetime.now()
                            )
                        elif cup_type == 'is_gc':
                            te = TournamentEvent(
                                tournament=tournament_obj,
                                tournament_shared=tournament_obj,
                                season_tournament_category_id=cat['id'],
                                season_cup_german_championship_id=gbo_data['id'],
                                season_tournament_id=season_tourn['id'],
                                name=to_tourn['name'],
                                category=tcat,
                                start_ts=datetime.fromtimestamp(start_ts),
                                end_ts=datetime.fromtimestamp(end_ts),
                                max_number_teams=16,
                                last_sync_at=datetime.now()
                            )
                        elif cup_type == 'is_sub':
                            te = TournamentEvent(
                                tournament=tournament_obj,
                                tournament_shared=tournament_obj,
                                season_tournament_category_id=cat['id'],
                                sub_season_cup_tournament_id=gbo_data['id'],
                                season_tournament_id=season_tourn['id'],
                                name=to_tourn['name'],
                                category=tcat,
                                start_ts=datetime.fromtimestamp(start_ts),
                                end_ts=datetime.fromtimestamp(end_ts),
                                max_number_teams=16,
                                last_sync_at=datetime.now()
                            )
                        if te:
                            #te.save()
                            #te.related_tournaments.set([tournament_obj])
                            new_events.append(te)
                    else:
                        te = tevents[0]
                        te.tournament = tournament_obj
                        te.name = to_tourn['name']
                        te.category = tcat
                        te.start_ts = datetime.fromtimestamp(start_ts)
                        te.end_ts = datetime.fromtimestamp(end_ts)
                        te.max_number_teams = 16
                        te.last_sync_at = datetime.now()
                        te.save()
                        if not te.related_tournaments.filter(id=tournament_obj.id).exists():
                            te.related_tournaments.add(tournament_obj)
                        te.save()

                    # team sync
                    data = gbo_data['seasonTeamCupTournamentRankings']
                    if te:
                        sync_only_teams(gbouser, te, data, cup_type)

            # Bulk create new events
            if new_events:
                TournamentEvent.objects.bulk_create(new_events)
                created_events = list(TournamentEvent.objects.filter(
                    tournament=tournament_obj,
                    # add other unique filters if needed
                ).order_by('id'))
                # Optionally, sync teams for new events (if needed)
                for te in created_events:
                    te.related_tournaments.set([tournament_obj])
                    data = None
                    if cup_type == 'is_cup' and te.season_cup_tournament_id == gbo_data['id']:
                        data = gbo_data['seasonTeamCupTournamentRankings']
                    elif cup_type == 'is_gc' and te.season_cup_german_championship_id == gbo_data['id']:
                        data = gbo_data['seasonTeamCupTournamentRankings']
                    elif cup_type == 'is_sub' and te.sub_season_cup_tournament_id == gbo_data['id']:
                        data = gbo_data['seasonTeamCupTournamentRankings']
                    if data is not None:
                        sync_only_teams(gbouser, te, data, cup_type)

    except Exception as ex:
        print(ex)
    print("EXIT update_user_tournament_events", datetime.now())
    end = time.time()
    execution_time = end - begin
    print("EXIT update_user_tournament_events", execution_time)
    return execution_time

def update_user_tournament_events_OLD(gbouser, to_tourn):
    begin = time.time()
    print("ENTER update_user_tournament_events" , datetime.now())
    try:
        if type(gbouser) is GBOUser:
            gbouser = gbouser.__dict__
        if type(to_tourn) is Tournament:
            to_tourn = to_tourn.__dict__
        cup_type = 'is_cup'
        if to_tourn['season_cup_tournament_id'] != 0:
            gbo_data = gbouser['gbo_data_all']
            cup_type = 'is_cup'
        elif to_tourn['season_cup_german_championship_id'] != 0:
            gbo_data = gbouser['gbo_gc_data']
            cup_type = 'is_gc'
        elif to_tourn['sub_season_cup_tournament_id'] != 0:
            gbo_data = gbouser['gbo_sub_data']
            cup_type = 'is_sub'
        else:
            print("No ID to any gbo tournament")
            return
        if not gbo_data['isError']:
            gbo_data = gbo_data['message']

            # Prefetch all categories for this tournament
            category_ids = [cat['category']['id'] for gbot in gbo_data for cat in gbot['seasonTournament']['seasonTournamentCategories']]
            existing_cats = TournamentCategory.objects.filter(gbo_category_id__in=category_ids)
            cat_map = {(cat.gbo_category_id, cat.classification, cat.name, cat.category): cat for cat in existing_cats}

            for gbot in gbo_data:
                print('gbo_data' , datetime.now())
                season_tourn = gbot['seasonTournament']
                if cup_type == 'is_cup' and season_tourn['id'] != to_tourn['season_tournament_id']:
                    continue
                elif cup_type == 'is_gc' and season_tourn['id'] != to_tourn['season_german_championship_id']:
                    continue
                elif cup_type == 'is_sub':
                    continue
                    
                # read dates
                if not season_tourn['seasonTournamentWeeks']:
                    print("Not weeks defined")
                start_ts = int(season_tourn['seasonTournamentWeeks'][0]['seasonWeek']['start_at_ts'])/1000
                end_ts = int(season_tourn['seasonTournamentWeeks'][0]['seasonWeek']['end_at_ts'])/1000

                # scan categories and update/create events
                for cat in season_tourn['seasonTournamentCategories']:
                    print('category ' + str(cat['category']) , datetime.now())
                    for cat in season_tourn['seasonTournamentCategories']:
                        abbrv = 'M' if cat['category']['gender']['name'] == 'man' else 'W'
                        cat_key = (cat['category']['id'], cat['category']['name'], cat['category']['gender']['name'], cat['category']['gender']['name'])
                        tcat = cat_map.get(cat_key)
                        if not tcat:
                            tcat = TournamentCategory(
                                gbo_category_id=cat['category']['id'],
                                classification=cat['category']['name'],
                                name=cat['category']['gender']['name'],
                                category=cat['category']['gender']['name'],
                                abbreviation=abbrv,
                                season_tournament_category_id=cat['id']
                            )
                            tcat.save()
                            cat_map[cat_key] = tcat


                    if cup_type == 'is_cup':
                        tevents = TournamentEvent.objects.filter(tournament_id=to_tourn['id'], category=tcat, season_cup_tournament_id=gbot['id'])
                    elif cup_type == 'is_gc':
                        tevents = TournamentEvent.objects.filter(tournament_id=to_tourn['id'], category=tcat, season_cup_german_championship_id=gbot['id'])
                    elif cup_type == 'is_sub':
                        tevents = TournamentEvent.objects.filter(tournament_id=to_tourn['id'], category=tcat, sub_season_cup_tournament_id=gbot['id'])
                    else:
                        tevents = TournamentEvent.objects.none()
                    te = TournamentEvent()
                    if tevents.count() == 0:  
                        if cup_type == 'is_cup':
                            te = TournamentEvent(tournament_id=to_tourn['id'],
                                season_tournament_category_id=cat['id'],
                                season_cup_tournament_id=gbot['id'],
                                season_tournament_id=season_tourn['id'],
                                name=to_tourn['name'],
                                category=tcat,
                                start_ts=datetime.fromtimestamp(start_ts),
                                end_ts=datetime.fromtimestamp(end_ts),
                                max_number_teams=16,
                                last_sync_at=datetime.now())
                        elif cup_type == 'is_gc':
                            te = TournamentEvent(tournament_id=to_tourn['id'],
                                season_tournament_category_id=cat['id'],
                                season_cup_german_championship_id=gbot['id'],
                                season_tournament_id=season_tourn['id'],
                                name=to_tourn['name'],
                                category=tcat,
                                start_ts=datetime.fromtimestamp(start_ts),
                                end_ts=datetime.fromtimestamp(end_ts),
                                max_number_teams=16,
                                last_sync_at=datetime.now())
                        elif cup_type == 'is_sub':
                            te = TournamentEvent(tournament_id=to_tourn['id'],
                                season_tournament_category_id=cat['id'],
                                sub_season_cup_tournament_id=gbot['id'],
                                season_tournament_id=season_tourn['id'],
                                name=to_tourn['name'],
                                category=tcat,
                                start_ts=datetime.fromtimestamp(start_ts),
                                end_ts=datetime.fromtimestamp(end_ts),
                                max_number_teams=16,
                                last_sync_at=datetime.now())
                        
                    else:
                        te = tevents.first()
                        te.tournament_id=to_tourn['id']
                        te.name=to_tourn['name']
                        te.category=tcat
                        te.start_ts=datetime.fromtimestamp(start_ts)
                        te.end_ts=datetime.fromtimestamp(end_ts)
                        te.max_number_teams=16
                        te.last_sync_at=datetime.now()
                    te.save()

                    # team
                    #if cup_type == 'is_cup':
                    #    data = SWS.getSeasonTeamCupTournamentRanking(gbouser)
                    #elif cup_type == 'is_gc':
                    #    data = SWS.getSeasonTeamCupChampionshipRanking(gbouser)
                    #elif cup_type == 'is_sub':
                    #    data = SWS.getSeasonTeamSubCupTournamentRanking(gbouser)
                    #else:
                    #    data = {}
                    #
                    #if data['isError'] is True:
                    #    print(data['message'])
                    #    continue
                    data = gbot['seasonTeamCupTournamentRankings']
                    sync_only_teams(gbouser, te, data, cup_type)              
    except Exception as ex:
        print(ex)               
    print("EXIT update_user_tournament_events" , datetime.now())
    end = time.time()
    execution_time = end - begin
    print("EXIT update_user_tournament_events" , execution_time)
    return execution_time



def sync_teams_of_tevent(gbouser, tevent):
    begin = time.time()
    print("ENTER sync_teams_of_tevent", datetime.now())
    result = {'isError': False, 'msg': ''}
    try:
        # Prefetch all teams, players, and coaches for this event
        team_qs = Team.objects.select_related("tournament_event").filter(tournament_event=tevent)
        all_teams = list(team_qs)
        team_map = {}
        for team in all_teams:
            if tevent.season_cup_tournament_id:
                team_map[team.season_team_cup_tournament_ranking_id] = team
            elif tevent.season_cup_german_championship_id:
                team_map[team.season_team_cup_championship_ranking_id] = team
            elif getattr(tevent, 'sub_season_cup_tournament_id', None):
                team_map[getattr(team, 'season_team_sub_cup_tournament_ranking_id', None)] = team

        # Determine cup_type and get SWS data
        to_tourn = tevent.tournament.__dict__
        if to_tourn['season_cup_tournament_id'] != 0:
            cup_type = 'is_cup'
            data, execution_time = SWS.syncTournamentData(gbouser, tevent.tournament.season.gbo_season_id)
            ranking_field = 'season_team_cup_tournament_ranking_id'
        elif to_tourn['season_cup_german_championship_id'] != 0:
            cup_type = 'is_gc'
            data, execution_time = SWS.syncTournamentGCData(gbouser, tevent.tournament.season.gbo_season_id)
            ranking_field = 'season_team_cup_championship_ranking_id'
        elif to_tourn.get('sub_season_cup_tournament_id', 0) != 0:
            cup_type = 'is_sub'
            data, execution_time = SWS.syncTournamentSubData(gbouser, tevent.tournament.season.gbo_season_id)
            ranking_field = 'season_team_sub_cup_tournament_ranking_id'
        else:
            result['isError'] = True
            result['msg'] = 'Unknown cup type'
            return result

        if type(gbouser) is GBOUser:
            gbouser = gbouser.__dict__
        if data['isError']:
            result['isError'] = True
            result['msg'] = 'Could not get data from SWS endpoint /season/cup-tournaments/to/'
            return result

        gbo_data = data['message'][0]
        ranking_ids = set(r['id'] for r in gbo_data['seasonTeamCupTournamentRankings'])

        # Prepare for bulk operations
        teams_to_update = []
        teams_to_create = []
        teams_to_delete = []
        seen_team_ids = set()

        for ranking in gbo_data['seasonTeamCupTournamentRankings']:
            if  ranking['seasonTeam']['team']['category']['id'] != tevent.category.gbo_category_id:
                continue
            team = team_map.get(ranking['id'])
            if not team:
                # Create new team
                team = Team(
                    tournament_event=tevent,
                    name=ranking['seasonTeam']['team']['name'],
                    abbreviation=ranking['seasonTeam']['team']['name_abbreviated'],
                    gbo_team=ranking['seasonTeam']['team']['id'],
                    category=tevent.category,
                    is_dummy=False
                )
                setattr(team, ranking_field, ranking['id'])
                if cup_type == 'is_cup':
                    team.season_cup_tournament_id = tevent.season_cup_tournament_id
                elif cup_type == 'is_gc':
                    team.season_cup_german_championship_id = tevent.season_cup_german_championship_id
                teams_to_create.append(team)
            else:
                # Update existing team
                team.name = ranking['seasonTeam']['team']['name']
                team.abbreviation = ranking['seasonTeam']['team']['name_abbreviated']
                team.gbo_team = ranking['seasonTeam']['team']['id']
                team.category = tevent.category
                team.is_dummy = False
                setattr(team, ranking_field, ranking['id'])
                if cup_type == 'is_cup':
                    team.season_cup_tournament_id = tevent.season_cup_tournament_id
                elif cup_type == 'is_gc':
                    team.season_cup_german_championship_id = tevent.season_cup_german_championship_id
                teams_to_update.append(team)
                seen_team_ids.add(team.id)

        # Teams to delete: those not in the incoming data
        for team in all_teams:
            if team.id not in seen_team_ids and not team.is_dummy:
                teams_to_delete.append(team.id)

        # Bulk operations
        if teams_to_create:
            Team.objects.bulk_create(teams_to_create)
        if teams_to_update:
            Team.objects.bulk_update(
                teams_to_update,
                fields=[
                    "name", "abbreviation", "gbo_team", "category", "is_dummy",
                    "season_team_cup_tournament_ranking_id", "season_cup_tournament_id",
                    "season_team_cup_championship_ranking_id", "season_cup_german_championship_id",
                    "season_team_sub_cup_tournament_ranking_id"
                ]
            )
        if teams_to_delete:
            Team.objects.filter(id__in=teams_to_delete).delete()

        all_players = list(Player.objects.filter(tournament_event=tevent))
        all_coaches = list(Coach.objects.filter(tournament_event=tevent))
        players_by_team = defaultdict(list)
        for player in all_players:
            players_by_team[player.team_id].append(player)

        coaches_by_team = defaultdict(list)
        for coach in all_coaches:
            coaches_by_team[coach.team_id].append(coach)


        team_qs = Team.objects.select_related("tournament_event", "category").filter(tournament_event=tevent)
        all_teams = list(team_qs)
        cat = tevent.category
        for ranking in gbo_data['seasonTeamCupTournamentRankings']:
            if ranking['seasonTeam']['team']['category']['gender']['id'] != tevent.category.gbo_category_id:
                continue
            sync_single_team_by_ranking(ranking, tevent, all_teams, cup_type, gbouser, True, all_players, all_coaches, cat)

        # Dummy teams update (if needed)
        dummy_teams = [team for team in all_teams if team.is_dummy and team.tournament_event.id == tevent.id]
        sct_id = None
        if cup_type == 'is_cup':
            sct_id = tevent.season_cup_tournament_id
            for dummy in dummy_teams:
                dummy.season_cup_tournament_id = sct_id
            Team.objects.bulk_update(dummy_teams, ("season_cup_tournament_id",))
        elif cup_type == 'is_gc':
            sct_id = tevent.season_cup_german_championship_id
            for dummy in dummy_teams:
                dummy.season_cup_german_championship_id = sct_id
            Team.objects.bulk_update(dummy_teams, ("season_cup_german_championship_id",))

        sync_referees_of_tournament(gbo_data, tevent.tournament)

    except Exception as ex:
        print(traceback.format_exc())
        result['isError'] = True
        result['msg'] = str(ex)

    print("EXIT sync_teams_of_tevent", datetime.now())
    end = time.time()
    execution_time = end - begin
    print("EXIT sync_teams_of_tevent", execution_time)
    return result


def sync_teams_of_tevent_OLD(gbouser, tevent):
    result = {'isError': False, 'msg': ''}
    team_data_q = Team.objects.select_related("tournament_event").filter(tournament_event=tevent).prefetch_related(
            Prefetch("player_set", queryset=Player.objects.select_related("tournament_event").all(), to_attr="players"),
            Prefetch("coach_set", queryset=Coach.objects.select_related("tournament_event").all(), to_attr="coaches")
        ).all()
    my_team_data = [team for team in team_data_q if not team.is_dummy]
    team_ids = [team.id for team in my_team_data]
    
    try:
        
        to_tourn = tevent.tournament.__dict__
        if to_tourn['season_cup_tournament_id'] != 0:
            #gbo_data = gbouser['gbo_data_all']
            cup_type = 'is_cup'
            data, execution_time = SWS.syncTournamentData(gbouser, tevent.tournament.season.gbo_season_id)
            ranking_ids = [team.season_team_cup_tournament_ranking_id for team in my_team_data]
        elif to_tourn['season_cup_german_championship_id'] != 0:
            #gbo_data = gbouser['gbo_gc_data']
            cup_type = 'is_gc'
            data, execution_time = SWS.syncTournamentGCData(gbouser, tevent.tournament.season.gbo_season_id)
            ranking_ids = [team.season_team_cup_championship_ranking_id for team in my_team_data]
        elif to_tourn['sub_season_cup_tournament_id'] != 0:
            #gbo_data = gbouser['gbo_sub_data']
            cup_type = 'is_sub'
            data, execution_time = SWS.syncTournamentSubData(gbouser, tevent.tournament.season.gbo_season_id)
            ranking_ids = [team.season_team_cup_tournament_ranking_id for team in my_team_data]

        if type(gbouser) is GBOUser:
            gbouser = gbouser.__dict__
        gbo_data = []
        if data['isError'] == True:
            result['isError'] =  True
            result['msg'] = 'Could not get data from SWS endpoint /season/cup-tournaments/to/'
            return result
        else:
            gbo_data = data['message'][0]
        
        sct_id = 0
        if cup_type == 'is_cup':
            sct_id = tevent.season_cup_tournament_id
        elif cup_type == 'is_gc':
            sct_id = tevent.season_cup_german_championship_id
        elif cup_type == 'is_sub':
            sct_id = tevent.sub_season_cup_tournament_id

        all_players = list(Player.objects.filter(tournament_event=tevent))
        all_coaches = list(Coach.objects.filter(tournament_event=tevent))

        season_cup_tourn_id_for_dummy = 0;
        for ranking in gbo_data['seasonTeamCupTournamentRankings']:
            if not ranking['id'] in ranking_ids:
                continue
            result = sync_single_team_by_ranking(ranking, tevent, my_team_data, cup_type, gbouser, True, all_players, all_coaches, tevent.category)
            if result['isError'] == True:
                break

        sync_referees_of_tournament(gbo_data, tevent.tournament)

    except Exception as ex:
        print(traceback.format_exc())
        result['isError'] =  True
        result['msg'] = ex.args[1]
    return result

def sync_teams_of_game(gbouser, game):
    result = {'isError': False, 'msg': ''}
    
    if game.team_a is None and game.team_st_a is not None:
        game.team_a = game.team_st_a.team
    
    if game.team_b is None and game.team_st_b is not None:
        game.team_b = game.team_st_b.team
    game.save()
    team_ids = [game.team_a.id, game.team_b.id]
    ranking_ids = [game.team_a.season_team_cup_tournament_ranking_id, game.team_b.season_team_cup_tournament_ranking_id]
    try:
        #data, execution_time = SWS.syncTournamentData(gbouser, game.tournament.season.gbo_season_id)


        to_tourn = game.tournament_event.tournament.__dict__
        if to_tourn['season_cup_tournament_id'] != 0:
            #gbo_data = gbouser['gbo_data_all']
            cup_type = 'is_cup'
            data, execution_time = SWS.syncTournamentData(gbouser, game.tournament.season.gbo_season_id)
            #ranking_ids = [team.season_team_cup_tournament_ranking_id for team in my_team_data]
        elif to_tourn['season_cup_german_championship_id'] != 0:
            #gbo_data = gbouser['gbo_gc_data']
            cup_type = 'is_gc'
            data, execution_time = SWS.syncTournamentGCData(gbouser, game.tournament.season.gbo_season_id)
            #ranking_ids = [team.season_team_cup_championship_ranking_id for team in my_team_data]
        elif to_tourn['sub_season_cup_tournament_id'] != 0:
            #gbouser['gbo_sub_data']
            cup_type = 'is_sub'
            data, execution_time = SWS.syncTournamentSubData(gbouser, game.tournament.season.gbo_season_id)
            #ranking_ids = [team.season_team_cup_tournament_ranking_id for team in my_team_data]
        gbo_data = []
        if data['isError'] == True:
            result['isError'] =  True
            result['msg'] = 'Could not get data from SWS endpoint /season/cup-tournaments/to/'
            return result
        else:
            gbo_data = data['message'][0]

        if type(gbouser) is GBOUser:
            gbouser = gbouser.__dict__

        to_tourn = game.tournament.__dict__
        if to_tourn['season_cup_tournament_id'] != 0:
            #gbo_data = gbouser['gbo_data_all']
            cup_type = 'is_cup'
        elif to_tourn['season_cup_german_championship_id'] != 0:
            #gbouser['gbo_gc_data']
            cup_type = 'is_gc'
        elif to_tourn['sub_season_cup_tournament_id'] != 0:
            #gbo_data = gbouser['gbo_sub_data']
            cup_type = 'is_sub'
        
        team_data_q = Team.objects.select_related("tournament_event").filter(tournament_event=game.tournament_event).prefetch_related(
            Prefetch("player_set", queryset=Player.objects.select_related("tournament_event").all(), to_attr="players"),
            Prefetch("coach_set", queryset=Coach.objects.select_related("tournament_event").all(), to_attr="coaches")
        ).filter(id__in=team_ids)

        my_team_data = [team for team in team_data_q if not team.is_dummy]
        my_dummy_team_data = [team for team in team_data_q if team.is_dummy and team.tournament_event.id == game.tournament_event.id]

        sct_id = 0
        if cup_type == 'is_cup':
            sct_id = game.tournament_event.season_cup_tournament_id
        elif cup_type == 'is_gc':
            sct_id = game.tournament_event.season_cup_german_championship_id
        elif cup_type == 'is_sub':
            sct_id = game.tournament_event.sub_season_cup_tournament_id

        all_players = list(Player.objects.filter(tournament_event=game.tournament_event))
        all_coaches = list(Coach.objects.filter(tournament_event=game.tournament_event))

        season_cup_tourn_id_for_dummy = 0;
        for ranking in gbo_data['seasonTeamCupTournamentRankings']:
            if not ranking['id'] in ranking_ids:
                continue
            result = sync_single_team_by_ranking(ranking, game.tournament_event, my_team_data, cup_type, gbouser, True, all_players, all_coaches, game.tournament_event.category)
            if result['isError'] == True:
                break
    except Exception as ex:
        print(traceback.format_exc())
        result['isError'] =  True
        result['msg'] = ex.message
    return result

def sync_only_teams(gbouser, tevent, data, cup_type):
    print('ENTER sync_only_teams', datetime.now())
    try:
        # Prefetch all teams for this event
        team_qs = Team.objects.select_related("tournament_event").filter(tournament_event=tevent)
        team_qs = team_qs.prefetch_related(
            Prefetch("player_set", queryset=Player.objects.select_related("tournament_event").all(), to_attr="players"),
            Prefetch("coach_set", queryset=Coach.objects.select_related("tournament_event").all(), to_attr="coaches")
        )
        all_teams = list(team_qs)
        team_map = {}
        for team in all_teams:
            if cup_type == 'is_cup':
                team_map[team.season_team_cup_tournament_ranking_id] = team
            elif cup_type == 'is_gc':
                team_map[team.season_team_cup_championship_ranking_id] = team
            elif cup_type == 'is_sub':
                team_map[team.season_team_sub_cup_tournament_ranking_id] = team

        # Prepare sets for fast lookup
        ranking_ids = set()
        for ranking in data:
            ranking_ids.add(ranking['id'])

        # Track teams to keep, update, create, and delete
        teams_to_update = []
        teams_to_create = []
        teams_to_delete = []
        seen_team_ids = set()

        for ranking in data:
            team = team_map.get(ranking['id'])
            if not team:
                # Create new team
                team = Team(
                    tournament_event=tevent,
                    name=ranking['seasonTeam']['team']['name'],
                    abbreviation=ranking['seasonTeam']['team']['name_abbreviated'],
                    gbo_team=ranking['seasonTeam']['team']['id'],
                    category=tevent.category,
                    is_dummy=False
                )
                if cup_type == 'is_cup':
                    team.season_team_cup_tournament_ranking_id = ranking['id']
                    team.season_cup_tournament_id = tevent.season_cup_tournament_id
                elif cup_type == 'is_gc':
                    team.season_team_cup_championship_ranking_id = ranking['id']
                    team.season_cup_german_championship_id = tevent.season_cup_german_championship_id
                elif cup_type == 'is_sub':
                    team.season_team_sub_cup_tournament_ranking_id = ranking['id']
                    team.sub_season_cup_tournament_id = tevent.sub_season_cup_tournament_id
                teams_to_create.append(team)
            else:
                # Update existing team
                team.name = ranking['seasonTeam']['team']['name']
                team.abbreviation = ranking['seasonTeam']['team']['name_abbreviated']
                team.gbo_team = ranking['seasonTeam']['team']['id']
                team.category = tevent.category
                team.is_dummy = False
                if cup_type == 'is_cup':
                    team.season_team_cup_tournament_ranking_id = ranking['id']
                    team.season_cup_tournament_id = tevent.season_cup_tournament_id
                elif cup_type == 'is_gc':
                    team.season_team_cup_championship_ranking_id = ranking['id']
                    team.season_cup_german_championship_id = tevent.season_cup_german_championship_id
                elif cup_type == 'is_sub':
                    team.season_team_sub_cup_tournament_ranking_id = ranking['id']
                    team.sub_season_cup_tournament_id = tevent.sub_season_cup_tournament_id
                teams_to_update.append(team)
                seen_team_ids.add(team.id)

        # Teams to delete: those not in the incoming data
        for team in all_teams:
            if team.id not in seen_team_ids and not team.is_dummy:
                teams_to_delete.append(team.id)

        # Bulk operations
        if teams_to_create:
            Team.objects.bulk_create(teams_to_create)
        if teams_to_update:
            Team.objects.bulk_update(
                teams_to_update,
                fields=[
                    "name", "abbreviation", "gbo_team", "category", "is_dummy",
                    "season_team_cup_tournament_ranking_id", "season_cup_tournament_id",
                    "season_team_cup_championship_ranking_id", "season_cup_german_championship_id",
                    "season_team_sub_cup_tournament_ranking_id"
                ]
            )
        if teams_to_delete:
            Team.objects.filter(id__in=teams_to_delete).delete()

        # Dummy teams update (if needed)
        dummy_teams = [team for team in all_teams if team.is_dummy and team.tournament_event.id == tevent.id]
        sct_id = None
        if cup_type == 'is_cup':
            sct_id = tevent.season_cup_tournament_id
            for dummy in dummy_teams:
                dummy.season_cup_tournament_id = sct_id
            Team.objects.bulk_update(dummy_teams, ("season_cup_tournament_id",))
        elif cup_type == 'is_gc':
            sct_id = tevent.season_cup_german_championship_id
            for dummy in dummy_teams:
                dummy.season_cup_german_championship_id = sct_id
            Team.objects.bulk_update(dummy_teams, ("season_cup_german_championship_id",))

        print('SUCCESS')
    except Exception as ex:
        print(traceback.format_exc())
    return

def sync_only_teams_OLD(gbouser, tevent, data, cup_type):
    print('ENTER sync_only_teams' , datetime.now())
    try:        
        team_data_q = Team.objects.select_related("tournament_event").filter(tournament_event=tevent).prefetch_related(
            Prefetch("player_set", queryset=Player.objects.select_related("tournament_event").all(), to_attr="players"),
            Prefetch("coach_set", queryset=Coach.objects.select_related("tournament_event").all(), to_attr="coaches")
        ).all()
        my_team_data = [team for team in team_data_q if not team.is_dummy]
        my_dummy_team_data = [team for team in team_data_q if team.is_dummy and team.tournament_event.id == tevent.id]    
        
        sct_id = 0
        if cup_type == 'is_cup':
            sct_id = tevent.season_cup_tournament_id
        elif cup_type == 'is_gc':
            sct_id = tevent.season_cup_german_championship_id
        elif cup_type == 'is_sub':
            sct_id = tevent.sub_season_cup_tournament_id

        all_players = list(Player.objects.filter(tournament_event=tevent))
        all_coaches = list(Coach.objects.filter(tournament_event=tevent))

        season_cup_tourn_id_for_dummy = 0;
        for ranking in data: #team_info['seasonTeamCupTournamentRankings']:
            result = sync_single_team_by_ranking(ranking, tevent, my_team_data, cup_type, gbouser, False, all_players, all_coaches, tevent.category)
            if not result['isError']:
                my_team_data = [ x for x in my_team_data if x is not result['act_team'] ]

        for team in my_team_data:
            team.delete()

        for dummy in my_dummy_team_data:
            if cup_type == 'is_cup':
                dummy.season_cup_tournament_id = sct_id #season_cup_tourn_id_for_dummy
                continue
            if cup_type == 'is_gc':
                dummy.season_cup_german_championship_id = sct_id #season_cup_tourn_id_for_dummy
                continue
            if cup_type == 'is_sub':
                continue
        if cup_type == 'is_cup':
            Team.objects.bulk_update(my_dummy_team_data, ("season_cup_tournament_id",))
        if cup_type == 'is_gc':
            Team.objects.bulk_update(my_dummy_team_data, ("season_cup_german_championship_id",))
        print('SUCCESS')
    except Exception as ex:
        print(traceback.format_exc())
    return

def sync_teams(gbouser, tevent, data, cup_type):
    print('ENTER sync_teams' , datetime.now())
    try:        
        team_data_q = Team.objects.select_related("tournament_event").filter(tournament_event=tevent).prefetch_related(
            Prefetch("player_set", queryset=Player.objects.select_related("tournament_event").all(), to_attr="players"),
            Prefetch("coach_set", queryset=Coach.objects.select_related("tournament_event").all(), to_attr="coaches")
        ).all()
        my_team_data = [team for team in team_data_q if not team.is_dummy]
        my_dummy_team_data = [team for team in team_data_q if team.is_dummy and team.tournament_event.id == tevent.id]    
        
        sct_id = 0
        if cup_type == 'is_cup':
            sct_id = tevent.season_cup_tournament_id
        elif cup_type == 'is_gc':
            sct_id = tevent.season_cup_german_championship_id
        elif cup_type == 'is_sub':
            sct_id = tevent.sub_season_cup_tournament_id

        all_players = list(Player.objects.filter(tournament_event=tevent))
        all_coaches = list(Coach.objects.filter(tournament_event=tevent))

        season_cup_tourn_id_for_dummy = 0;
        for ranking in data: #team_info['seasonTeamCupTournamentRankings']:
            result = sync_single_team_by_ranking(ranking, tevent, my_team_data, cup_type, gbouser, True, all_players, all_coaches, tevent.category)

        for team in my_team_data:
            team.delete()

        for dummy in my_dummy_team_data:
            if cup_type == 'is_cup':
                dummy.season_cup_tournament_id = sct_id #season_cup_tourn_id_for_dummy
                continue
            if cup_type == 'is_gc':
                dummy.season_cup_german_championship_id = sct_id #season_cup_tourn_id_for_dummy
                continue
            if cup_type == 'is_sub':
                continue
        if cup_type == 'is_cup':
            Team.objects.bulk_update(my_dummy_team_data, ("season_cup_tournament_id",))
        if cup_type == 'is_gc':
            Team.objects.bulk_update(my_dummy_team_data, ("season_cup_german_championship_id",))
        print('SUCCESS')
    except Exception as ex:
        print(traceback.format_exc())
    return

def sync_single_team_by_ranking(ranking, tevent, team_data_django, cup_type, gbouser, doPlayersSync, all_players=None, all_coaches=None, category=None):
    """
    Sync a single team (and optionally its players/coaches) by ranking.
    Optimized for performance with batch operations and reduced DB queries.
    """
    result = {'isError': False, 'msg': ''}
    
    # Early validation to avoid unnecessary processing
    if not category or category.gbo_category_id != ranking['seasonTeam']['team']['category']['id']:
        result['isError'] = True
        result['msg'] = 'tevent.category.gbo_category_id id is not equal season_team.team.category.id'
        return result

    # Define ranking field name based on cup_type
    ranking_field = {
        'is_cup': 'season_team_cup_tournament_ranking_id',
        'is_gc': 'season_team_cup_championship_ranking_id',
        'is_sub': 'season_team_sub_cup_tournament_ranking_id'
    }.get(cup_type)
    
    if not ranking_field:
        result['isError'] = True
        result['msg'] = f'Unknown cup_type: {cup_type}'
        return result

    # Fast dictionary lookup for team instead of linear search
    team_mapping = {
        getattr(t, ranking_field): t for t in team_data_django 
        if hasattr(t, ranking_field) and getattr(t, ranking_field) is not None
    }
    act_team = team_mapping.get(ranking['id'])

    # Prepare common team data
    team_data = {
        'tournament_event': tevent,
        'name': ranking['seasonTeam']['team']['name'],
        'abbreviation': ranking['seasonTeam']['team']['name_abbreviated'],
        'gbo_team': ranking['seasonTeam']['team']['id'],
        'category': category,
        'is_dummy': False,
        ranking_field: ranking['id']
    }
    
    # Add cup type specific fields
    if cup_type == 'is_cup':
        team_data['season_cup_tournament_id'] = tevent.tournament.season_cup_tournament_id
    elif cup_type == 'is_gc':
        team_data['season_cup_german_championship_id'] = tevent.tournament.season_cup_german_championship_id

    # Create team if not found
    if act_team is None:
        act_team = Team.objects.create(**team_data)
    else:
        # Only update if changed (track changes)
        changed_fields = []
        for field, value in team_data.items():
            if field != 'tournament_event' and getattr(act_team, field) != value:
                setattr(act_team, field, value)
                changed_fields.append(field)
                
        if changed_fields:
            act_team.save(update_fields=changed_fields)

    result['act_team'] = act_team

    # If we don't need player sync, return early
    if not doPlayersSync:
        return result

    # --- Prepare player & coach sync ---
    season_team_id = act_team.season_team_id or ranking['seasonTeam']['id']
    act_team.season_team_id = season_team_id  # Make sure it's set
    
    # --- COACH SYNC ---
    # Use provided coaches or fetch them
    if all_coaches is not None:
        coaches = [c for c in all_coaches if c.team_id == act_team.id]
    else:
        coaches = list(Coach.objects.filter(team=act_team))
    
    # Create lookup dictionaries by (season_coach_id, season_team_id)
    coach_dict = {(c.season_coach_id, c.season_team_id): c for c in coaches}
    coach_updates = []
    coach_creates = []
    coach_ids_seen = set()
    
    # Process coaches in batch
    for row in ranking.get('seasonCoachesInTournament', []):
        if 'seasonCoach' not in row:
            continue
            
        season_coach = row['seasonCoach']
        key = (season_coach['id'], season_team_id)
        coach_ids_seen.add(key)
        coach = coach_dict.get(key)
        
        user_data = season_coach['seasonSubject']['subject']['user']
        name = strip_accents(user_data['family_name'])
        first_name = strip_accents(user_data['name'])
        gbo_position = season_coach['seasonSubject']['subject']['subjectLevel']['name']
        
        if coach is None:
            # Create new coach
            coach_creates.append(Coach(
                tournament_event=tevent,
                team=act_team,
                name=name,
                first_name=first_name,
                gbo_position=gbo_position,
                season_team_id=season_team_id,
                season_coach_id=season_coach['id']
            ))
        else:
            # Only update if there are changes
            updated = False
            if coach.name != name:
                coach.name = name
                updated = True
            if coach.first_name != first_name:
                coach.first_name = first_name
                updated = True
            if coach.gbo_position != gbo_position:
                coach.gbo_position = gbo_position
                updated = True
                
            if updated:
                coach_updates.append(coach)
    
    # --- PLAYER SYNC ---
    # Get team data from API (only if needed)
    if doPlayersSync:
        response = SWS.getSeasonTeam(gbouser, ranking['seasonTeam']['id'])
        season_team_data = {'seasonPlayers': []} 
        if response and not response[0]['isError']:
            season_team_data = response[0]['message']
        
        # Use provided players or fetch them
        if all_players is not None:
            players = [p for p in all_players if p.team_id == act_team.id]
        else:
            players = list(Player.objects.filter(team=act_team))
            
        # Create lookup dictionary
        player_dict = {(p.season_player_id, p.season_team_id): p for p in players}
        player_updates = []
        player_creates = []
        player_ids_seen = set()
        
        # Build a set of active player IDs for faster lookups
        active_player_ids = {
            ap.get('seasonPlayer', {}).get('id') 
            for ap in ranking.get('seasonPlayersInTournament', [])
            if ap.get('seasonPlayer')
        }
        
        # Process players in batch
        for season_player in season_team_data['seasonPlayers']:
            key = (season_player['id'], season_team_id)
            player_ids_seen.add(key)
            player = player_dict.get(key)
            
            # Extract common data
            user_data = season_player['seasonSubject']['subject']['user']
            name = strip_accents(user_data['family_name'])
            first_name = strip_accents(user_data['name'])
            gbo_position = season_player['seasonSubject']['subject']['subjectLevel']['name']
            number = season_player['number']
            is_active = season_player['id'] in active_player_ids
            
            # Parse birthday safely
            birthday = None
            try:
                birthday = datetime.strptime(user_data['birthday'], "%Y-%m-%dT%H:%M:%S.%fZ").date()
            except Exception:
                pass
                
            if player is None:
                # Create new player
                new_player = Player(
                    tournament_event=tevent,
                    team=act_team,
                    first_name=first_name,
                    name=name,
                    gbo_position=gbo_position,
                    number=number,
                    season_team_id=season_team_id,
                    season_player_id=season_player['id'],
                    subject_data=season_player['seasonSubject'],
                    is_active=is_active,
                )
                if birthday:
                    new_player.birthday = birthday
                player_creates.append(new_player)
            else:
                # Only update if there are changes
                updated = False
                if player.name != name:
                    player.name = name
                    updated = True
                if player.first_name != first_name:
                    player.first_name = first_name
                    updated = True
                if player.gbo_position != gbo_position:
                    player.gbo_position = gbo_position
                    updated = True
                if player.number != number:
                    player.number = number
                    updated = True
                if player.is_active != is_active:
                    player.is_active = is_active
                    updated = True
                if birthday and player.birthday != birthday:
                    player.birthday = birthday
                    updated = True
                    
                if updated:
                    player_updates.append(player)

    # --- Perform all DB operations in a single transaction ---
    with transaction.atomic():
        # Coaches operations
        if coach_creates:
            Coach.objects.bulk_create(coach_creates)
        if coach_updates:
            Coach.objects.bulk_update(coach_updates, ["name", "first_name", "gbo_position"])
        
        # Delete coaches that no longer exist
        coach_ids_to_delete = [c.id for c_key, c in coach_dict.items() if c_key not in coach_ids_seen]
        if coach_ids_to_delete:
            Coach.objects.filter(id__in=coach_ids_to_delete).delete()

        # Players operations (only if we're syncing players)
        if doPlayersSync:
            if player_creates:
                Player.objects.bulk_create(player_creates)
            if player_updates:
                Player.objects.bulk_update(player_updates, ["name", "first_name", "gbo_position", "number", "is_active", "birthday"])
            
            # Delete players that no longer exist
            player_ids_to_delete = [p.id for p_key, p in player_dict.items() if p_key not in player_ids_seen]
            if player_ids_to_delete:
                Player.objects.filter(id__in=player_ids_to_delete).delete()

    return result


def sync_single_team_by_ranking_NEWR(ranking, tevent, team_data_django, cup_type, gbouser, doPlayersSync, all_players=None, all_coaches=None, category=None):
    """
    Sync a single team (and optionally its players/coaches) by ranking.
    """
    result = {'isError': False, 'msg': ''}
    if category.gbo_category_id != ranking['seasonTeam']['team']['category']['id']:
        result['isError'] = True
        result['msg'] = 'tevent.category.gbo_category_id id is not equal season_team.team.category.id'
        return result

    # Fast lookup for team
    if cup_type == 'is_cup':
        act_team = next((x for x in team_data_django if x.season_team_cup_tournament_ranking_id == ranking['id']), None)
    elif cup_type == 'is_gc':
        act_team = next((x for x in team_data_django if x.season_team_cup_championship_ranking_id == ranking['id']), None)
    elif cup_type == 'is_sub':
        act_team = next((x for x in team_data_django if x.season_team_sub_cup_tournament_ranking_id == ranking['id']), None)
    else:
        act_team = None

    # Create team if not found
    if act_team is None:
        team_kwargs = {
            'tournament_event': tevent,
            'name': ranking['seasonTeam']['team']['name'],
            'abbreviation': ranking['seasonTeam']['team']['name_abbreviated'],
            'gbo_team': ranking['seasonTeam']['team']['id'],
            'category': category,
            'is_dummy': False,
        }
        if cup_type == 'is_cup':
            team_kwargs['season_team_cup_tournament_ranking_id'] = ranking['id']
            team_kwargs['season_cup_tournament_id'] = tevent.tournament.season_cup_tournament_id
        elif cup_type == 'is_gc':
            team_kwargs['season_team_cup_championship_ranking_id'] = ranking['id']
            team_kwargs['season_cup_german_championship_id'] = tevent.tournament.season_cup_german_championship_id
        elif cup_type == 'is_sub':
            team_kwargs['season_team_sub_cup_tournament_ranking_id'] = ranking['id']
        act_team = Team.objects.create(**team_kwargs)
    else:
        # Only update if changed
        changed = False
        if act_team.name != ranking['seasonTeam']['team']['name']:
            act_team.name = ranking['seasonTeam']['team']['name']
            changed = True
        if act_team.abbreviation != ranking['seasonTeam']['team']['name_abbreviated']:
            act_team.abbreviation = ranking['seasonTeam']['team']['name_abbreviated']
            changed = True
        if act_team.gbo_team != ranking['seasonTeam']['team']['id']:
            act_team.gbo_team = ranking['seasonTeam']['team']['id']
            changed = True
        if act_team.category != category:
            act_team.category = category
            changed = True
        if act_team.is_dummy:
            act_team.is_dummy = False
            changed = True
        if changed:
            act_team.save(update_fields=['name', 'abbreviation', 'gbo_team', 'category', 'is_dummy'])

    result['act_team'] = act_team

    if not doPlayersSync:
        return result

    # Use the provided lists if available, else fallback to ORM
    if all_players is not None:
        players = [p for p in all_players if p.team_id == act_team.id]
    else:
        players = list(act_team.player_set.all())

    if all_coaches is not None:
        coaches = [c for c in all_coaches if c.team_id == act_team.id]
    else:
        coaches = list(act_team.coach_set.all())

    # --- Sync Coaches ---
    # Build a dict for fast lookup
    existing_coaches = { (c.season_coach_id, c.season_team_id): c for c in coaches }
    incoming_coach_ids = set()
    coach_bulk_create = []
    coach_bulk_update = []

    for row in ranking.get('seasonCoachesInTournament', []):
        if 'seasonCoach' not in row:
            continue
        season_coach = row['seasonCoach']
        key = (season_coach['id'], act_team.season_team_id)
        incoming_coach_ids.add(key)
        coach = existing_coaches.get(key)
        if coach is None:
            coach = Coach(
                tournament_event=tevent,
                team=act_team,
                name=strip_accents(season_coach['seasonSubject']['subject']['user']['family_name']),
                first_name=strip_accents(season_coach['seasonSubject']['subject']['user']['name']),
                gbo_position=season_coach['seasonSubject']['subject']['subjectLevel']['name'],
                season_team_id=act_team.season_team_id,
                season_coach_id=season_coach['id']
            )
            coach_bulk_create.append(coach)
        else:
            updated = False
            if coach.name != strip_accents(season_coach['seasonSubject']['subject']['user']['family_name']):
                coach.name = strip_accents(season_coach['seasonSubject']['subject']['user']['family_name'])
                updated = True
            if coach.first_name != strip_accents(season_coach['seasonSubject']['subject']['user']['name']):
                coach.first_name = strip_accents(season_coach['seasonSubject']['subject']['user']['name'])
                updated = True
            if coach.gbo_position != season_coach['seasonSubject']['subject']['subjectLevel']['name']:
                coach.gbo_position = season_coach['seasonSubject']['subject']['subjectLevel']['name']
                updated = True
            if updated:
                coach_bulk_update.append(coach)

    # Delete coaches not in incoming data
    to_delete_coaches = [c for k, c in existing_coaches.items() if k not in incoming_coach_ids]

    # --- Sync Players ---
    if doPlayersSync:
        response = SWS.getSeasonTeam(gbouser, ranking['seasonTeam']['id'])
        if response and not response[0]['isError']:
            season_team_data = response[0]['message']
        else:
            season_team_data = {'seasonPlayers': []}

        existing_players = { (p.season_player_id, p.season_team_id): p for p in players }
        incoming_player_ids = set()
        player_bulk_create = []
        player_bulk_update = []

        for season_player in season_team_data['seasonPlayers']:
            key = (season_player['id'], act_team.season_team_id)
            incoming_player_ids.add(key)
            player = existing_players.get(key)
            if player is None:
                player = Player(
                    tournament_event=tevent,
                    team=act_team,
                    first_name=strip_accents(season_player['seasonSubject']['subject']['user']['name']),
                    name=strip_accents(season_player['seasonSubject']['subject']['user']['family_name']),
                    gbo_position=season_player['seasonSubject']['subject']['subjectLevel']['name'],
                    number=season_player['number'],
                    season_team_id=act_team.season_team_id,
                    season_player_id=season_player['id'],
                    subject_data=season_player['seasonSubject'],
                )
                # Parse birthday
                try:
                    player.birthday = datetime.strptime(season_player['seasonSubject']['subject']['user']['birthday'], "%Y-%m-%dT%H:%M:%S.%fZ").date()
                except Exception:
                    pass
                # Set is_active
                player.is_active = any(
                    ap.get('seasonPlayer', {}).get('id') == season_player['id']
                    for ap in ranking.get('seasonPlayersInTournament', [])
                )
                player_bulk_create.append(player)
            else:
                updated = False
                if player.name != strip_accents(season_player['seasonSubject']['subject']['user']['family_name']):
                    player.name = strip_accents(season_player['seasonSubject']['subject']['user']['family_name'])
                    updated = True
                if player.first_name != strip_accents(season_player['seasonSubject']['subject']['user']['name']):
                    player.first_name = strip_accents(season_player['seasonSubject']['subject']['user']['name'])
                    updated = True
                if player.gbo_position != season_player['seasonSubject']['subject']['subjectLevel']['name']:
                    player.gbo_position = season_player['seasonSubject']['subject']['subjectLevel']['name']
                    updated = True
                if player.number != season_player['number']:
                    player.number = season_player['number']
                    updated = True
                # Parse birthday
                try:
                    birthday = datetime.strptime(season_player['seasonSubject']['subject']['user']['birthday'], "%Y-%m-%dT%H:%M:%S.%fZ").date()
                    if player.birthday != birthday:
                        player.birthday = birthday
                        updated = True
                except Exception:
                    pass
                # Set is_active
                is_active = any(
                    ap.get('seasonPlayer', {}).get('id') == season_player['id']
                    for ap in ranking.get('seasonPlayersInTournament', [])
                )
                if player.is_active != is_active:
                    player.is_active = is_active
                    updated = True
                if updated:
                    player_bulk_update.append(player)

        # Delete players not in incoming data
        to_delete_players = [p for k, p in existing_players.items() if k not in incoming_player_ids]

    # --- Bulk DB Operations ---
    with transaction.atomic():
        if coach_bulk_create:
            Coach.objects.bulk_create(coach_bulk_create)
        if coach_bulk_update:
            Coach.objects.bulk_update(coach_bulk_update, ["name", "first_name", "gbo_position"])
        if to_delete_coaches:
            Coach.objects.filter(id__in=[c.id for c in to_delete_coaches]).delete()

        if doPlayersSync:
            if player_bulk_create:
                Player.objects.bulk_create(player_bulk_create)
            if player_bulk_update:
                Player.objects.bulk_update(player_bulk_update, ["name", "first_name", "gbo_position", "number", "is_active", "birthday"])
            if to_delete_players:
                Player.objects.filter(id__in=[p.id for p in to_delete_players]).delete()

    return result

def sync_single_team_by_ranking_OLD(ranking, tevent, team_data_django, cup_type, gbouser, doPlayersSync):
    print('team ranking: ' + ranking['seasonTeam']['team']['name'])
    result = {'isError': False, 'msg':''}
    if tevent.category.gbo_category_id != ranking['seasonTeam']['team']['category']['id']:
        result['isError'] = True
        result['msg'] = 'tevent.category.gbo_category_id id is not equal season_team.team.category.id'
        return result
    print('MATCH team ranking: ' + ranking['seasonTeam']['team']['name'])
    #season_cup_tourn_id_for_dummy = ranking['seasonCupTournament']['id']
    player_bulk_update_list = []
    player_bulk_create_list = []
    coach_bulk_update_list = []
    coach_bulk_create_list = []
    players_list = []
    coaches_list = []

    if cup_type == 'is_cup':
        act_team = next((x for x in team_data_django if x.season_team_cup_tournament_ranking_id==ranking['id']), None)
    elif cup_type == 'is_gc':
        act_team = next((x for x in team_data_django if x.season_team_cup_championship_ranking_id==ranking['id']), None)
    elif cup_type == 'is_sub':
        act_team = next((x for x in team_data_django if x.season_team_cup_tournament_ranking_id==ranking['id']), None)
 
    result['act_team'] = act_team
    if not act_team is None:
        players_list = act_team.players
        coaches_list = act_team.coaches
    if act_team is None and cup_type == 'is_cup':
        act_team, cr = Team.objects.get_or_create(season_team_cup_tournament_ranking_id=ranking['id'],
            tournament_event=tevent)
    elif act_team is None and  cup_type == 'is_gc':
        act_team, cr = Team.objects.get_or_create(season_team_cup_championship_ranking_id=ranking['id'],
            tournament_event=tevent)
    elif act_team is None and  cup_type == 'is_sub':
        act_team, cr = Team.objects.get_or_create(season_team_sub_cup_tournament_ranking_id=ranking['id'],
            tournament_event=tevent)
    elif act_team is None:
        result['isError'] = True
        result['msg'] = 'Could not find team with ranking.id'
        return result
    
    act_team.gbo_team = ranking['seasonTeam']['team']['id']
    act_team.season_team_id = ranking['seasonTeam']['id']
    act_team.season_team_cup_tournament_ranking_id = ranking['id']
    if cup_type == 'is_cup':
        act_team.season_team_cup_tournament_ranking_id = ranking['id']
        act_team.season_cup_tournament_id = tevent.tournament.season_cup_tournament_id
    elif cup_type == 'is_gc':
        act_team.season_team_cup_championship_ranking_id = ranking['id']
        act_team.season_cup_german_championship_id = tevent.tournament.season_cup_german_championship_id
    elif cup_type == 'is_sub':
        act_team.season_team_sub_cup_tournament_ranking_id = ranking['id']
    act_team.name = ranking['seasonTeam']['team']['name']
    act_team.abbreviation = ranking['seasonTeam']['team']['name_abbreviated']
    act_team.category = tevent.category
    act_team.is_dummy = False
    #team_bulk_list.append(act_team)
    act_team.save()

    season_team = ranking['seasonTeam']

    response = SWS.getSeasonTeam(gbouser, season_team['id'])
    if len(response) > 0 and response[0]['isError'] == False:
        season_team_data = response[0]['message']
    else:
        season_team_data = {'seasonPlayers':[]}

    # Coaches
    if 'seasonCoachesInTournament' in ranking:
        for row in ranking['seasonCoachesInTournament']:
            if not 'seasonCoach' in row:
                continue
            season_coach = row['seasonCoach']
            print('CheckCoach:' + str(act_team.season_team_id) + ' id:' + str(season_coach['id']) + ' Name: ' + str(season_coach['seasonSubject']['subject']['user']['name']) + ' ' + str(season_coach['seasonSubject']['subject']['user']['family_name']))
            cr = False
            act_coach = next((x for x in coaches_list if x.tournament_event.id==tevent.id and x.season_team_id==act_team.season_team_id and x.season_coach_id==season_coach['id']), None)
            if act_coach is None:
                act_coach = Coach(tournament_event=tevent, season_team_id=act_team.season_team_id, season_coach_id=season_coach['id'])
                cr = True
            else:
                coaches_list = [ x for x in coaches_list if x is not act_coach ]
            act_coach.tournament_event = tevent
            act_coach.team = act_team
            act_coach.name = strip_accents(season_coach['seasonSubject']['subject']['user']['family_name'])
            act_coach.first_name = strip_accents(season_coach['seasonSubject']['subject']['user']['name'])
            act_coach.gbo_position = season_coach['seasonSubject']['subject']['subjectLevel']['name']
            act_coach.season_team_id = act_team.season_team_id
            act_coach.season_coach_id = season_coach['id']
            if cr:
                coach_bulk_create_list.append(act_coach)
            else:
                coach_bulk_update_list.append(act_coach)
            #act_coach.save()
    if len(coach_bulk_create_list) > 0:
        Coach.objects.bulk_create(coach_bulk_create_list)
    if len(coach_bulk_update_list) > 0:
        Coach.objects.bulk_update(coach_bulk_update_list, ("tournament_event", "team", "name", "first_name", "gbo_position","season_team_id", "season_coach_id",))  
    for co in coaches_list:
        co.delete()

    if not doPlayersSync:
        return result

    for season_player in season_team_data['seasonPlayers']:
        print('CheckPlayer:' + str(act_team.season_team_id) + ' id:' + str(season_player['id']) + ' #' + str(season_player['number'])+ ' Name: ' + str(season_player['seasonSubject']['subject']['user']['name']) + ' ' + str(season_player['seasonSubject']['subject']['user']['family_name']))
        cr = False
        act_player = next((x for x in players_list if x.tournament_event.id==tevent.id and x.season_team_id==act_team.season_team_id and x.season_player_id==season_player['id']), None)
        if act_player is None:
            #act_player, cr = Player.objects.get_or_create(tournament_event=tevent, season_team_id=act_team.season_team_id, season_player_id=season_player['id'])
            act_player = Player(tournament_event=tevent, season_team_id=act_team.season_team_id, season_player_id=season_player['id'])
            cr = True
        else:
            players_list = [ x for x in players_list if x is not act_player ]
        act_player.tournament_event = tevent
        act_player.team = act_team
        birthday_string =  ''
        try:
            birthday_string = season_player['seasonSubject']['subject']['user']['birthday']
            act_player.birthday = datetime.strptime(birthday_string, "%Y-%m-%dT%H:%M:%S.%fZ").date()
        except ValueError:
            print("Cannor parse birthday: " + birthday_string)
        act_player.name = strip_accents(season_player['seasonSubject']['subject']['user']['family_name'])
        act_player.first_name = strip_accents(season_player['seasonSubject']['subject']['user']['name'])
        act_player.gbo_position = season_player['seasonSubject']['subject']['subjectLevel']['name']
        act_player.subject_data = season_player['seasonSubject']
        is_active = False
        for activeplayer in ranking['seasonPlayersInTournament']:
            if activeplayer['seasonPlayer'] is None:
                continue
            if activeplayer['seasonPlayer']['id'] == season_player['id']:
                is_active = True
                break
        act_player.is_active = is_active
        act_player.number = season_player['number']
        act_player.season_team_id = act_team.season_team_id
        act_player.season_player_id = season_player['id']
        if cr:
            player_bulk_create_list.append(act_player)
        else:
            player_bulk_update_list.append(act_player)
    
    if len(player_bulk_create_list) > 0:
        Player.objects.bulk_create(player_bulk_create_list)
    if len(player_bulk_update_list) > 0:
        Player.objects.bulk_update(player_bulk_update_list, ("tournament_event", "team", "name", "first_name", "gbo_position", "is_active", "number","season_team_id", "season_player_id", "subject_data", "birthday",))
    for pl in players_list:
        pl.delete()
    
    return result

def sync_referees_of_tournament(gbodata, tournament):
    print('ENTER sync_referees_of_tournament')
    if (gbodata is None or 
        'seasonTournament' not in gbodata or
        'seasonTournamentCriteriaSubjects' not in gbodata['seasonTournament']):
        print('Insufficient data in sync_referees_of_tournament')
        return
    
    try:
        # Get all referees in a single query
        existing_referees = {
            ref.gbo_subject_id: ref 
            for ref in Referee.objects.filter(tournament=tournament)
        }
        
        referees_to_create = []
        referees_to_update = []
        
        # Process all entries in a single pass
        for entry in gbodata['seasonTournament']['seasonTournamentCriteriaSubjects']:
            if ('seasonSubject' not in entry or
                not entry['seasonSubject'] or
                'subject' not in entry['seasonSubject'] or
                not entry['seasonSubject']['subject'] or
                'authGroup' not in entry['seasonSubject']['subject'] or
                not entry['seasonSubject']['subject']['authGroup'] or
                entry['seasonSubject']['subject']['authGroup'].get('name_code') != 'referee'):
                continue
                
            subject = entry['seasonSubject']['subject']
            subject_id = subject['id']
            first_name = subject['user']['name']
            family_name = subject['user']['family_name']
            
            # Create abbreviation once
            abbr = ''
            if first_name and family_name:
                abbr = first_name[0].upper() + family_name[0].upper()
                
            if subject_id not in existing_referees:
                # Create new referee
                referees_to_create.append(Referee(
                    tournament=tournament,
                    abbreviation=abbr,
                    gbo_subject_id=subject_id,
                    name=family_name,
                    first_name=first_name
                ))
            else:
                # Update existing referee
                referee = existing_referees[subject_id]
                updated = False
                
                if referee.first_name != first_name:
                    referee.first_name = first_name
                    updated = True
                    
                if referee.name != family_name:
                    referee.name = family_name
                    updated = True
                    
                if first_name and family_name and referee.abbreviation != abbr:
                    referee.abbreviation = abbr
                    updated = True
                    
                if updated:
                    referees_to_update.append(referee)
        
        # Perform bulk operations
        if referees_to_create:
            Referee.objects.bulk_create(referees_to_create)
            print(f'Created {len(referees_to_create)} new referees')
            
        if referees_to_update:
            Referee.objects.bulk_update(
                referees_to_update, 
                fields=['first_name', 'name', 'abbreviation']
            )
            print(f'Updated {len(referees_to_update)} referees')

    except Exception as ex:
        print(traceback.format_exc())




def sync_referees_of_tournament_OLD(gbodata, tournament):
    print('ENTER sync_referees_of_tournament')
    if gbodata is None:
        print('gbo data none sync_referees_of_tournament')
        return
    
    if 'seasonTournament' not in gbodata:
        print('seasonTournament not in data sync_referees_of_tournament')
        return

    if 'seasonTournamentCriteriaSubjects' not in gbodata['seasonTournament']:
        print('seasonTournamentCriteriaSubjects not in data sync_referees_of_tournament')
        return
    
    try:
        to_referees = [ref for ref in  Referee.objects.filter(tournament=tournament).all()]
        for entry in gbodata['seasonTournament']['seasonTournamentCriteriaSubjects']:
            if 'seasonSubject' in entry:
                seasonSub = entry['seasonSubject']
                if seasonSub and 'subject' in seasonSub and seasonSub['subject'] and \
                   'authGroup' in seasonSub['subject'] and seasonSub['subject']['authGroup'] and \
                   seasonSub['subject']['authGroup'].get('name_code') == 'referee':
                    print('Found referee')
                    subject = seasonSub['subject']
                    to_ref = find_referee_by_gbo_subject_id(to_referees, subject['id'])

                    if to_ref is None:
                        abbr = ''
                        if subject['user']['name'] and subject['user']['family_name']:
                            abbr = subject['user']['name'][0].upper() + subject['user']['family_name'][0].upper()
                        Referee.objects.create(
                            tournament=tournament,
                            abbreviation=abbr,
                            gbo_subject_id=subject['id'],
                            name=subject['user']['family_name'],
                            first_name=subject['user']['name']
                        )
                    else:
                        to_ref.first_name = subject['user']['name']
                        to_ref.name = subject['user']['family_name']
                        if to_ref.first_name and to_ref.name:
                            to_ref.abbreviation = to_ref.first_name[0].upper() + to_ref.name[0].upper()
                        to_ref.save()

    except Exception as ex:
        print(traceback.format_exc())

def find_referee_by_gbo_subject_id(referees, gbo_subject_id):
    for referee in referees:
        if referee.gbo_subject_id == gbo_subject_id:
            return referee
    return None

def strip_accents(text):

    try:
        text = str(bytes(text,'utf-8'), 'utf-8')
    except NameError: # unicode is a default on python 3 
        pass

    text = unicodedata.normalize('NFD', text)\
           .encode('ascii', 'ignore')\
           .decode("utf-8")

    return str(text)

def update_team(gbouser, team_id):
    return

def reverse_querystring(view, urlconf=None, args=None, kwargs=None, current_app=None, query_kwargs=None):
    '''Custom reverse to handle query strings.
    Usage:
        reverse('app.views.my_view', kwargs={'pk': 123}, query_kwargs={'search': 'Bob'})
    '''
    base_url = reverse(view, urlconf=urlconf, args=args, kwargs=kwargs, current_app=current_app)
    if query_kwargs:
        return '{}?{}'.format(base_url, urlencode(query_kwargs))
    return base_url

def update_games_after_tstat_chg(tstat):
    try:
        games = Game.objects.select_related("team_st_a__team", "team_st_b__team").filter(tournament_event=tstat.tournament_event,
                                                                                        tournament_state=tstat.tournamentstate,
                                                                                        gamestate='APPENDING').all()

        bulk_list_games = []    
        for g in games:
            game_update = False
            if g.team_st_a.id == tstat.id:
                g.team_a = tstat.team
                game_update = True
            if g.team_st_b.id == tstat.id:
                g.team_b = tstat.team
                game_update = True
            if game_update:
                bulk_list_games.append(g)
        Game.objects.bulk_update(bulk_list_games,("team_a", "team_b"))
    except Exception as ex:
        print(ex)

        
def calculate_tstate(tstate):
    try:
        #ts = TournamentState.objects.get(id=tstate)

        tstats = list(TeamStats.objects.filter(tournamentstate=tstate))
        tstats_map = {ts.id: ts for ts in tstats}
        for ts in tstats:
            ts.number_of_played_games = 0
            ts.game_points = 0
            ts.game_points_bonus = 0
            ts.ranking_points = 0
            ts.sets_win = 0
            ts.sets_loose = 0
            ts.points_made = 0
            ts.points_received = 0
        TeamStats.objects.bulk_update(
            tstats,
            [
                "number_of_played_games", "game_points", "game_points_bonus",
                "ranking_points", "sets_win", "sets_loose", "points_made", "points_received"
            ]
        )
        #games = Game.objects.all().filter(tournament_event=ts.tournament_event,
        #                                  tournament_state=ts,
        #                                  gamestate='FINISHED')
        
        # Update APPENDING games' team_a/team_b in bulk
        games_app = list(Game.objects.select_related("team_st_a__team", "team_st_b__team")
                         .filter(tournament_event=tstate.tournament_event,
                                 tournament_state=tstate,
                                 gamestate='APPENDING'))
        for g in games_app:
            g.team_a = g.team_st_a.team
            g.team_b = g.team_st_b.team
        Game.objects.bulk_update(games_app, ("team_a", "team_b"))

        # Fetch all FINISHED games and related TeamStats in one go
        games = list(Game.objects.select_related("team_st_a", "team_st_b")
                     .filter(tournament_event=tstate.tournament_event,
                             tournament_state=tstate,
                             gamestate='FINISHED'))

        # Prepare in-memory stats update
        team_stats_updates = {}
        games_bulk_list = []
        num_finished_games = 0

        for g in games:
            team_a_stats = g.team_st_a
            team_b_stats = g.team_st_b
            iSetH = 0
            iSetA = 0

            # Calculate set wins
            if getIntVal(g.score_team_a_halftime_1) > getIntVal(g.score_team_b_halftime_1):
                iSetH += 1
            elif getIntVal(g.score_team_a_halftime_1) < getIntVal(g.score_team_b_halftime_1):
                iSetA += 1

            if getIntVal(g.score_team_a_halftime_2) > getIntVal(g.score_team_b_halftime_2):
                iSetH += 1
            elif getIntVal(g.score_team_a_halftime_2) < getIntVal(g.score_team_b_halftime_2):
                iSetA += 1

            if getIntVal(g.score_team_a_penalty) > getIntVal(g.score_team_b_penalty):
                iSetH += 1
            elif getIntVal(g.score_team_a_penalty) < getIntVal(g.score_team_b_penalty):
                iSetA += 1

            if iSetH == 0 and iSetA == 0:
                g.gamestate = GAMESTATE_CHOICES[0][0]
                games_bulk_list.append(g)
                continue

            # Update stats in memory
            for ts, sets_win, sets_loose, points_made, points_received, is_winner in [
                (team_a_stats, iSetH, iSetA,
                 getIntVal(g.score_team_a_halftime_1) + getIntVal(g.score_team_a_halftime_2) + getIntVal(g.score_team_a_penalty),
                 getIntVal(g.score_team_b_halftime_1) + getIntVal(g.score_team_b_halftime_2) + getIntVal(g.score_team_b_penalty),
                 iSetH > iSetA),
                (team_b_stats, iSetA, iSetH,
                 getIntVal(g.score_team_b_halftime_1) + getIntVal(g.score_team_b_halftime_2) + getIntVal(g.score_team_b_penalty),
                 getIntVal(g.score_team_a_halftime_1) + getIntVal(g.score_team_a_halftime_2) + getIntVal(g.score_team_a_penalty),
                 iSetA > iSetH)
            ]:
                if ts.id not in team_stats_updates:
                    team_stats_updates[ts.id] = {
                        "number_of_played_games": 0,
                        "game_points": 0,
                        "ranking_points": 0,
                        "sets_win": 0,
                        "sets_loose": 0,
                        "points_made": 0,
                        "points_received": 0,
                    }
                upd = team_stats_updates[ts.id]
                upd["number_of_played_games"] += 1
                if is_winner:
                    upd["game_points"] += 2
                    upd["ranking_points"] += 2
                upd["sets_win"] += sets_win
                upd["sets_loose"] += sets_loose
                upd["points_made"] += points_made
                upd["points_received"] += points_received

            g.gamingstate = 'Finished'
            g.calc_winner()
            games_bulk_list.append(g)
            num_finished_games += 1

        # Apply in-memory updates to TeamStats objects
        for ts in tstats:
            upd = team_stats_updates.get(ts.id)
            if upd:
                ts.number_of_played_games = upd["number_of_played_games"]
                ts.game_points = upd["game_points"]
                ts.ranking_points = upd["ranking_points"]
                ts.sets_win = upd["sets_win"]
                ts.sets_loose = upd["sets_loose"]
                ts.points_made = upd["points_made"]
                ts.points_received = upd["points_received"]

        TeamStats.objects.bulk_update(
            tstats,
            [
                "number_of_played_games", "game_points", "ranking_points",
                "sets_win", "sets_loose", "points_made", "points_received"
            ]
        )
        Game.objects.bulk_update(
            games_bulk_list,
            (
                "gamingstate", "score_team_a_halftime_1", "score_team_a_halftime_2", "score_team_a_penalty",
                "score_team_b_halftime_1", "score_team_b_halftime_2", "score_team_b_penalty",
                "setpoints_team_a", "setpoints_team_b", "winner_halftime_1", "winner_halftime_2", "winner"
            )
        )

        # Ranking calculation
        if not tstate.direct_compare and num_finished_games > 0:
            teamstats = list(_do_table_ordering(TeamStats.objects.filter(tournamentstate=tstate)))
            max_val = len(teamstats)
            for rank, tstat in enumerate(teamstats, start=1):
                tstat.ranking_points += max_val
                tstat.rank = rank
                max_val -= 1
            TeamStats.objects.bulk_update(teamstats, ("ranking_points", "rank"))
        elif num_finished_games > 0:
            check_direct_compare(tstate)
            teamstats = list(_do_table_ordering(TeamStats.objects.filter(tournamentstate=tstate)))
            max_val = len(teamstats)
            for rank, tstat in enumerate(teamstats, start=1):
                tstat.ranking_points += max_val
                tstat.rank = rank
                max_val -= 1
            TeamStats.objects.bulk_update(teamstats, ("ranking_points", "rank"))

    except Exception as e:
        print(e)
    finally:
        print('')

def create_global_pstats(tevent_id):
    try:
        tevent = TournamentEvent.objects.get(id=tevent_id)
        # Fetch all players for the event
        player_list = list(Player.objects.filter(tournament_event=tevent))
        if not player_list:
            return

        # Fetch all existing PlayerStats for these players and this event
        existing_stats = PlayerStats.objects.filter(
            tournament_event=tevent,
            player__in=player_list,
            is_ranked=True
        ).select_related('player')

        # Build a set of (player_id) for which PlayerStats already exist
        existing_player_ids = set(ps.player_id for ps in existing_stats)

        # Prepare PlayerStats to create in bulk
        to_create = [
            PlayerStats(tournament_event=tevent, player=pl, is_ranked=True)
            for pl in player_list if pl.id not in existing_player_ids
        ]

        if to_create:
            PlayerStats.objects.bulk_create(to_create, batch_size=100)

    except Exception as e:
        print(e)
    finally:
        print('')

def create_global_pstats_of_game(game):
    try:
        tevent = game.tournament_event  # Use the event from the game
        player_list = list(Player.objects.filter(tournament_event=tevent))
        if not player_list:
            return

        # Fetch all existing PlayerStats for these players and this event
        existing_stats = PlayerStats.objects.filter(
            tournament_event=tevent,
            player__in=player_list,
            is_ranked=True
        ).select_related('player')

        # Build a set of player IDs for which PlayerStats already exist
        existing_player_ids = set(ps.player_id for ps in existing_stats)

        # Prepare PlayerStats to create in bulk
        to_create = [
            PlayerStats(tournament_event=tevent, player=pl, is_ranked=True)
            for pl in player_list if pl.id not in existing_player_ids
        ]

        if to_create:
            PlayerStats.objects.bulk_create(to_create, batch_size=100)

    except Exception as e:
        print(e)
    finally:
        print('')

def recalc_global_pstats(tevent_id):
    print('recalc_global_pstats tevent_id=' + str(tevent_id))
    try:
        tevent = TournamentEvent.objects.get(id=tevent_id)
        # Fetch all players for the event
        player_list = list(Player.objects.filter(tournament_event=tevent))
        if not player_list:
            return

        # Fetch all PlayerStats for this event
        global_pstats = list(PlayerStats.objects.select_related('player').filter(
            tournament_event=tevent, is_ranked=True
        ))
        pstats = list(PlayerStats.objects.select_related('player').filter(
            tournament_event=tevent, is_ranked=False
        ))

        # Build lookup dictionaries
        global_pstats_by_player = {ps.player_id: ps for ps in global_pstats}
        pstats_by_player = defaultdict(list)
        for ps in pstats:
            pstats_by_player[ps.player_id].append(ps)

        # Prepare fields to update
        fields = [
            'score', 'spin_success', 'spin_try', 'one_try', 'one_success',
            'suspension', 'redcard', 'block_success', 'goal_keeper_success',
            'season_cup_tournament_id', 'season_cup_german_championship_id',
            'season_player_id', 'season_team_id', 'gbo_category_id', 'games_played',
            'kempa_try', 'kempa_success', 'shooter_try', 'shooter_success',
            'sixm_try', 'sixm_success'
        ]

        # Update global stats in memory
        for pl in player_list:
            gl_stat = global_pstats_by_player.get(pl.id)
            if not gl_stat:
                continue
            stats = pstats_by_player.get(pl.id, [])
            gl_stat.score = sum(s.score for s in stats)
            gl_stat.spin_try = sum(s.spin_try for s in stats)
            gl_stat.spin_success = sum(s.spin_success for s in stats)
            gl_stat.kempa_try = sum(s.kempa_try for s in stats)
            gl_stat.kempa_success = sum(s.kempa_success for s in stats)
            gl_stat.shooter_try = sum(s.shooter_try for s in stats)
            gl_stat.shooter_success = sum(s.shooter_success for s in stats)
            gl_stat.one_try = sum(s.one_try for s in stats)
            gl_stat.one_success = sum(s.one_success for s in stats)
            gl_stat.sixm_try = sum(s.sixm_try for s in stats)
            gl_stat.sixm_success = sum(s.sixm_success for s in stats)
            gl_stat.suspension = sum(s.suspension for s in stats)
            gl_stat.redcard = sum(s.redcard for s in stats)
            gl_stat.goal_keeper_success = sum(s.goal_keeper_success for s in stats)
            gl_stat.block_success = sum(s.block_success for s in stats)
            gl_stat.season_cup_tournament_id = tevent.season_cup_tournament_id
            gl_stat.season_cup_german_championship_id = tevent.season_cup_german_championship_id
            gl_stat.season_player_id = pl.season_player_id
            gl_stat.season_team_id = pl.season_team_id
            gl_stat.gbo_category_id = tevent.category.gbo_category_id
            gl_stat.games_played = len(stats)

        # Bulk update all global stats
        PlayerStats.objects.bulk_update(global_pstats, fields=fields)

    except Exception as e:
        print(e)
    finally:
        print('')
def _do_table_ordering(queryset):
    return queryset.extra(
        select={'points_difference': 'points_made - points_received'}
    ).extra(
        select={'sets_difference': 'sets_win - sets_loose'}
    ).extra(
        select={'game_points_sum': 'game_points + game_points_bonus'}
    ).order_by(
        '-game_points_sum', '-sets_difference', '-points_difference', '-points_made'
    )

def check_direct_compare(ts):

    # get
    if ts.direct_compare and Game.objects.all().filter(tournament_event=ts.tournament_event,
                                                       tournament_state=ts,
                                                       gamestate=GAMESTATE_CHOICES[2][1]).count() > 0:
        # detect direct compares
        g_pts = 0
        team_list = []
        # get all TeamStats in tourstate
        teamstats = TeamStats.objects.all().filter(tournament_event=ts.tournament_event, tournamentstate=ts)
        # clear all old  direct compare calcs
        teamstats.update(game_points_bonus=0)

        # loop over them and check for direct compare
        for teamstat in teamstats:
            # all teamstats with same game_points
            teamst = TeamStats.objects.all().filter(tournament_event=ts.tournament_event, tournamentstate=ts,
                                                    game_points=teamstat.game_points,
                                                    game_points_bonus=teamstat.game_points_bonus)
            if teamst.count() == 2:
                games = Game.objects.all().filter(Q(team_st_a=teamst[0]) | Q(team_st_b=teamst[0]),
                                                  tournament_event=ts.tournament_event, tournament_state=ts)
                games = games.filter(Q(team_st_a=teamst[1]) | Q(team_st_b=teamst[1]),
                                     gamestate=GAMESTATE_CHOICES[2][1])
                if games.count() > 0:
                    teamstat = TeamStats.objects.get(id=get_game_winner(games.get()))
                    teamstat.game_points_bonus = 1
                    teamstat.save()

            elif teamst.count() > 2:
                print("Oh my god")

def check_all_tournamentstate_finshed(tevent, states):
    #tstates = stages.tstates #TournamentState.objects.filter(tournament_event=tevent)
    ts_bulk_list = []
    for ts in states:
        games_played = 0
        for game in ts.games:
            if game.gamestate == GAMESTATE_CHOICES[2][1]:
                games_played = games_played + 1
        
        if games_played == len(ts.games):
            ts.is_finished = True
        else:
            ts.is_finished = False
        ts_bulk_list.append(ts)
        #ts.save(update_fields=['is_finished'])
    TournamentState.objects.bulk_update(ts_bulk_list, ("is_finished",))

def check_tournamentstate_finished(tevent, ts):

    post_save.disconnect(signals.ttt_changed, sender=TournamentTeamTransition)
    games_played = Game.objects.all().filter(tournament_event=tevent,
                                             tournament_state=ts,
                                             gamestate=GAMESTATE_CHOICES[2][1]).count()

    all_games = Game.objects.all().filter(tournament_event=tevent,
                                          tournament_state=ts).count()

    # check if all games are FINISHED
    if games_played == all_games:
        # get teamstats
        teamstats = TeamStats.objects.filter(tournament_event=tevent,
                                            tournamentstate=ts).order_by('-ranking_points')

        iRank = 1
        for stat in teamstats:
            # get TournamentTeamTransition
            trans = TournamentTeamTransition.objects.filter(tournament_event=tevent,
                                                            origin_ts_id=ts,
                                                            #is_executed=False,
                                                            origin_rank=iRank)

            if trans.count() > 0:
                trans = trans.get()
                if trans.target_rank > -1 and not trans.target_ts_id is None:
                    target_stat = TeamStats.objects.all().filter(tournament_event=tevent,
                                                                tournamentstate=trans.target_ts_id,
                                                                rank_initial=trans.target_rank)
                    if target_stat.count() == 1:
                        trans.is_executed = True
                        trans.save(update_fields=['is_executed'])

                        target_stat = target_stat.get()
                        target_stat.team = stat.team
                        target_stat.name_table = stat.team.name
                        if trans.keep_stats:
                            target_stat.number_of_played_games = 0
                            target_stat.sets_win = stat.sets_win
                            target_stat.sets_loose = stat.sets_loose
                            target_stat.points_made = stat.points_made
                            target_stat.points_received = stat.points_received
                            target_stat.game_points = stat.game_points
                        target_stat.game_points_bonus = 0
                        target_stat.ranking_points = 0
                        target_stat.save()
                #trans.is_executed = True
                #trans.save(update_fields=['is_executed'])

            iRank = iRank + 1

        # check if all trans of tstate are done
        num_trans = TournamentTeamTransition.objects.filter(tournament_event=tevent,
                                                            origin_ts_id=ts,
                                                            is_executed=False).count()
        if num_trans > 0:
            ts.transitions_done = False
        else:
            ts.transitions_done = True
        ts.is_finished = True
        ts.save(update_fields=['transitions_done', 'is_finished'])
    else:
        ts.is_finished = False
        ts.save(update_fields=['is_finished'])
    post_save.connect(signals.ttt_changed, sender=TournamentTeamTransition)

def get_tournament_info_json(tourn):
    tourn_data = Tournament.objects.prefetch_related(
            Prefetch("game_set", queryset=Game.objects.select_related("tournament", "tournament_event__category", "team_a", "team_b", "team_st_a__team", "team_st_b__team", "ref_a", "ref_b", "tournament_state__tournament_stage", "court")
                , to_attr="all_games"),
            Prefetch("tournamentevent_set", queryset=TournamentEvent.objects.select_related("tournament", "category").prefetch_related(
                Prefetch("tournamentstage_set", queryset=TournamentStage.objects.select_related("tournament_event__category").prefetch_related(
                    Prefetch("tournamentstate_set", queryset=TournamentState.objects.select_related("tournament_event__category", "tournament_stage").prefetch_related(
                        Prefetch("teamstats_set", queryset=TeamStats.objects.select_related("team").order_by("rank")
                        , to_attr="all_team_stats"))
                            , to_attr="all_tstates"))
                                , to_attr="all_tstages"),),
                to_attr="all_tevents"),
            Prefetch("court_set", queryset=Court.objects.select_related("tournament")
                , to_attr="all_courts"),
            Prefetch("referee_set", queryset=Referee.objects.select_related("tournament")
                , to_attr="all_refs")
                ).filter(id=tourn.id).first()
    if tourn_data is None:
        return '{}'
    return serialize_tournament_full(tourn_data)

def get_tournament_multi_info_json(tourns):
    # Ensure tourns is a list of Tournament objects or IDs
    tourn_ids = [t.id if hasattr(t, 'id') else t for t in tourns]
    tournaments = list(Tournament.objects.prefetch_related(
        Prefetch(
            "tournamentevent_set",
            queryset=TournamentEvent.objects.select_related("tournament", "category").prefetch_related(
                Prefetch("tournamentstage_set", queryset=TournamentStage.objects.select_related("tournament_event__category").prefetch_related(
                    Prefetch("tournamentstate_set", queryset=TournamentState.objects.select_related("tournament_event__category", "tournament_stage").prefetch_related(
                        Prefetch("teamstats_set", queryset=TeamStats.objects.select_related("team").order_by("rank"), to_attr="all_team_stats"))
                            , to_attr="all_tstates"))
                                , to_attr="all_tstages"),
            ),
            to_attr="all_tevents"
        ),
        Prefetch("game_set", queryset=Game.objects.select_related("tournament", "tournament_event__category", "team_a", "team_b", "team_st_a__team", "team_st_b__team", "ref_a", "ref_b", "tournament_state__tournament_stage", "court"), to_attr="all_games"),
        Prefetch("court_set", queryset=Court.objects.select_related("tournament"), to_attr="all_courts"),
        Prefetch("referee_set", queryset=Referee.objects.select_related("tournament"), to_attr="all_refs")
    ).filter(id__in=tourn_ids))

    # Collect all events from all tournaments
    all_events = []
    for t in tournaments:
        all_events.extend(getattr(t, "all_tevents", []))
    # Optionally, attach all_events to each tournament for downstream use
    for t in tournaments:
        t.all_tevents = all_events

    # Return serialized data for all tournaments (or just the events, as needed)
    return serialize_tournament_full(t)

def get_tournament_info_light_json(tourn):
    tourn_data = Tournament.objects.prefetch_related(
            Prefetch("tournamentevent_set", queryset=TournamentEvent.objects.select_related("tournament", "category").prefetch_related(
                Prefetch("tournamentstage_set", queryset=TournamentStage.objects.select_related("tournament_event__category").prefetch_related(
                    Prefetch("tournamentstate_set", queryset=TournamentState.objects.select_related("tournament_event__category", "tournament_stage").prefetch_related(
                        Prefetch("teamstats_set", queryset=TeamStats.objects.select_related("team").order_by("rank")
                        , to_attr="all_team_stats"))
                            , to_attr="all_tstates"))
                                , to_attr="all_tstages"),),
                to_attr="all_tevents"),
                ).filter(id=tourn.id).first()
    if tourn_data is None:
        return '{}'
    return serialize_tournament_light(tourn_data)

def create_teams_testdata(tevent):
    tevent = TournamentEvent.objects.get(id=tevent)
    tcat = TournamentCategory.objects.get(id=1)
    max_teams = tevent.max_number_teams
    names = ('DreamTeam', 'The Beachers','SuperStars','Beach Easy Team','DumpHeads','FlyingKack','The Gang','Loosers',)
    abb = ('DT', 'TBS','SuS','BET','DH','FK','TGA','Loo',)
    for iTeam in range(0, max_teams):
        act_team_st, cr = Team.objects.get_or_create(tournament_event=tevent,
                                                    name=names[iTeam],
                                                    abbreviation=abb[iTeam],
                                                    gbo_team=0,
                                                    category=tcat)
        act_team_st.save()
        for i in range(1, 21):
            act_player, cr = Player.objects.get_or_create(tournament_event=tevent,
                                                            first_name=f'FName{i}',
                                                            name=f'Name{i}',
                                                            team=act_team_st,
                                                            number=i)
            act_player.save()
    # girls
    tcat = TournamentCategory.objects.get(id=2)
    names = ('wDreamTeam', 'wThe Beachers','wSuperStars','wBeach Easy Team','wDumpHeads','wFlyingKack','wThe Gang','wLoosers',)
    abb = ('DT', 'TBS','SuS','BET','DH','FK','TGA','Loo',)
    for iTeam in range(0, max_teams):
        act_team_st, cr = Team.objects.get_or_create(tournament_event=tevent,
                                                    name=names[iTeam],
                                                    abbreviation=abb[iTeam],
                                                    gbo_team=0,
                                                    category=tcat)
        act_team_st.save()
        for i in range(1, 21):
            act_player, cr = Player.objects.get_or_create(tournament_event=tevent,
                                                            first_name=f'FName{i}',
                                                            name=f'Name{i}',
                                                            team=act_team_st,
                                                            number=i)
            act_player.save()

def get_game_winner(game):
    if game.winner_halftime_1 == game.winner_halftime_2:
        return game.winner_halftime_1
    else:
        return game.winner_penalty

def getIntVal(val):
    if val is not None:
        return val
    else:
        return 0

def set_seasoncupid_to_all_global_pstats(tevent, seasoncupid):
    global_pstats = PlayerStats.objects.select_related('player').filter(tournament_event=tevent, is_ranked=True)
    for ps in global_pstats:
        ps.season_cup_german_championship_id=seasoncupid
        ps.save()

def parse_time_from_picker(dt_str):
    # Try ISO format first
    try:
        return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        pass
    # Try US format
    try:
        return datetime.strptime(dt_str, '%m/%d/%Y %H:%M')
    except ValueError:
        pass
    # Try Django's parse_datetime (handles some ISO and RFC formats)
    dt = parse_datetime(dt_str)
    if dt:
        return dt
    # If all fail, raise an error
    raise ValueError(f"Unknown date format: {dt_str}")

def update_game_real_time_data(game_obj):
    print('ENTER')
    pstats_a = serialize_pstats(PlayerStats.objects.filter(
            tournament_event=game_obj.tournament_event,
            game=game_obj,
            player__team=game_obj.team_a,
            is_ranked=False
        ))
    pstats_b = serialize_pstats(PlayerStats.objects.filter(
        tournament_event=game_obj.tournament_event,
        game=game_obj,
        player__team=game_obj.team_b,
        is_ranked=False
    ))

    game_info = {
        "id": game_obj.id,
        "actualHalftimeSeconds": game_obj.act_time,
        "maxHalfTimeSeconds": game_obj.duration_of_halftime,
        "court": game_obj.court.name,
        "startTs": int(game_obj.starttime.timestamp()) if game_obj.starttime else None,
        "maxPenalty": game_obj.number_of_penalty_tries,
        "isFirstHalf": False,
        "isSecondHalf": False,
        "isPenalty": False,
        "teamA": {
            "dataChanged": True,
            "seasonTeamId": game_obj.team_a.season_team_id,
            "scoreFirstHalf": game_obj.score_team_a_halftime_1,
            "scoreSecondHalf": game_obj.score_team_a_halftime_2,
            "scorePenalty": game_obj.score_team_a_penalty,
            "penaltyCount": 0,#game_obj.penalty_count_team_a,
            "playersScore": pstats_a,
            },
        "teamB": {
            "dataChanged": True,
            "seasonTeamId": game_obj.team_b.season_team_id,
            "scoreFirstHalf": game_obj.score_team_b_halftime_1,
            "scoreSecondHalf": game_obj.score_team_b_halftime_2,
            "scorePenalty": game_obj.score_team_b_penalty,
            "penaltyCount": 0,#game_obj.penalty_count_team_b,
            "playersScore": pstats_b,
            },
        
    }
    return game_info #ujson.dumps(game_info, escape_forward_slashes=False)


def serialize_pstats(qs):
    return [
        {
            "score": getattr(pstat, "score", 0),
            "seasonPlayer": {
                "id": getattr(pstat, "season_player_id", 0),
                "number": getattr(pstat.player, "number", 0),
                "seasonSubject": getattr(pstat.player, "subject_data", {}),
                }
            #**{field.name: getattr(pstat, field.name) for field in pstat._meta.fields},
        }
        for pstat in qs.select_related("player")
    ]