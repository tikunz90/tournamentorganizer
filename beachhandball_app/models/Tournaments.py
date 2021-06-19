from django.db import models
from django.utils import timezone
from datetime import datetime

import jsonfield

from colorfield.fields import ColorField

from .choices import TOURNAMENT_STATE_CHOICES, TOURNAMENT_STAGE_TYPE_CHOICES, COLOR_CHOICES

from django_unixdatetimefield import UnixDateTimeField


class Tournament(models.Model):
    """Model of representing a Beachhandball Tournament. It is the frame for TournamentEvents

    A Tournament basically has a name. Organizer is subject_id of gbo TO
    """
    created_at = UnixDateTimeField(editable=False, default=timezone.now)

    organizer = models.SmallIntegerField(default=0)
    name = models.CharField(db_column='name', max_length=50)
    is_active = models.BooleanField(default=False)
    #address = AddressField(related_name='+', blank=True, null=True, on_delete=models.CASCADE)
    
    last_sync_at = UnixDateTimeField(editable=False, default=timezone.now)
    gbo_data = jsonfield.JSONField()
    gbo_gc_data = jsonfield.JSONField()
    gbo_sub_data = jsonfield.JSONField()
    season_tournament_id = models.IntegerField(default=0)
    season_cup_tournament_id = models.IntegerField(default=0)
    gbo_tournament_id = models.IntegerField(default=0)
    season_cup_german_championship_id = models.IntegerField(default=0)
    sub_season_cup_tournament_id = models.IntegerField(default=0)

    @property
    def name_short(self):
        return '{}'.format(self.name)

    def __unicode__(self):
        return '{}'.format(self.name)

    def __str__(self):
        return '{}'.format(self.name)

    class Meta:
        db_table = 'bh_tournament'


class TournamentSettings(models.Model):
    """Model of representing a Tournaments settings
    """
    created_at = UnixDateTimeField(editable=False, default=timezone.now)

    tournament = models.ForeignKey('Tournament', null=True, on_delete=models.CASCADE)
    
    first_game_slot = UnixDateTimeField(editable=True, default=timezone.now)
    actual_game_slot = UnixDateTimeField(editable=True, default=timezone.now)
    game_slot_counter = models.SmallIntegerField(default=0)
    game_slot_mins = models.SmallIntegerField(default=45)

    amount_players_report = models.SmallIntegerField(default=10)
    amount_officials_report = models.SmallIntegerField(default=2)

    def __unicode__(self):
        return 'Tsettings: {}'.format(self.tournament)

    def __str__(self):
        return 'Tsettings: {}'.format(self.tournament)

    class Meta:
        db_table = 'bh_tournament_settings'


class TournamentEvent(models.Model):
    """Model of representing a Beachhandball TournamentEvent.

    A TournamentEvent basically has a name and is restricted to teams to the according gender.
    """
    created_at = UnixDateTimeField(editable=False, default=timezone.now)

    tournament = models.ForeignKey('Tournament', null=True, on_delete=models.CASCADE)
    #season = models.ForeignKey('Season', null=True, related_name='+', on_delete=models.SET_NULL)
    category = models.ForeignKey('TournamentCategory', blank=True, null=True, on_delete=models.SET_NULL)

    name = models.CharField(db_column='name', max_length=50)

    start_ts = UnixDateTimeField(null=False, default=timezone.now)
    end_ts = UnixDateTimeField(null=False, default=timezone.now)

    max_number_teams = models.SmallIntegerField(default=0)
    is_in_configuration = models.BooleanField(default=False)

    logo = models.CharField(max_length=50, default='trophy')

    last_sync_at = UnixDateTimeField(editable=True, default=timezone.now)
    season_tournament_id = models.IntegerField(null=True, default=0)
    season_cup_tournament_id = models.IntegerField(null=True, default=0)
    season_tournament_category_id = models.IntegerField(null=True, default=0)
    season_cup_german_championship_id = models.IntegerField(default=0)
    sub_season_cup_tournament_id = models.IntegerField(default=0)

    @property
    def name_short(self):
        return '{} {}'.format(self.name, self.category)
    
    @property
    def get_final_tstate(self):
        return self.tournamentstate_set.filter(is_final=True)

    def __unicode__(self):
        return '({}) {} - {}  von {} - {}'.format(self.id, self.name, self.category, self.start_ts, self.end_ts)

    def __str__(self):
        return '({}) {} - {}  von {} - {}'.format(self.id, self.name, self.category, self.start_ts, self.end_ts)

    class Meta:
        db_table = 'bh_tournament_event'


class Court(models.Model):
    """The Court model represents a playing court on a tournament.

    It is related to a Tournament and has a name which is free definable 
    by tournament organizer. E.g. CenterCourt.

    For organization tool the court number is more important and has to be
    unique!

    """
    created_at = UnixDateTimeField(editable=False, default=timezone.now)

    tournament = models.ForeignKey('Tournament', null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    number = models.SmallIntegerField(default=0)

    def __str__(self):
        return '{} ({})'.format(self. name, self.number)

    class Meta:
        db_table = 'bh_courts'


class TournamentStage(models.Model):
    """ Defines Type of TS. E.g if it is a GroupStagec, KnockOut Phase
    """
    created_at = UnixDateTimeField(editable=False, default=timezone.now)

    tournament_event = models.ForeignKey('TournamentEvent', null=True, on_delete=models.CASCADE)
    name = models.CharField( max_length=50, default="")
    short_name = models.CharField( max_length=5, default="", help_text="You have 5 characters to describe this stage")
    tournament_stage = models.CharField(max_length=20, choices=TOURNAMENT_STAGE_TYPE_CHOICES, blank=True)
    order = models.SmallIntegerField(default=0)

    @property
    def get_tstates_without_finalranking(self):
        return self.tournamentstate_set.filter(is_final=False)

    def __str__(self):
        return '{} ({})'.format(self. name, self.tournament_event.name)

    class Meta:
        # managed = False
        db_table = 'bh_tournament_stage'


class TournamentState(models.Model):
    """ TournamentStates are the main instances of a tournament structure.
    It can be a Group, Quarterfinal, Semifinal, final etc.

    While a tournament is played teams will transit through the defined TSs
    to reach the final. The rules how they transit are defined by TournamentTeamTransition's.
    """
    created_at = UnixDateTimeField(editable=False, default=timezone.now)

    tournament_event = models.ForeignKey('TournamentEvent', null=True, on_delete=models.CASCADE)
    tournament_state = models.CharField(max_length=20, choices=TOURNAMENT_STATE_CHOICES, blank=True)
    tournament_stage = models.ForeignKey('TournamentStage', null=True, on_delete=models.CASCADE)
    name = models.CharField(db_column='name', max_length=50)
    abbreviation = models.CharField(max_length=10, null=True)
    max_number_teams = models.SmallIntegerField(default=0)
    min_number_teams = models.SmallIntegerField(default=0)
    hierarchy = models.SmallIntegerField(default=0)
    grid_row = models.SmallIntegerField(default=0)
    grid_col = models.SmallIntegerField(default=0)
    direct_compare = models.BooleanField(default=False)
    is_populated = models.BooleanField(default=False)
    is_final = models.BooleanField(default=False)
    is_finished = models.BooleanField(default=False)
    transitions_done = models.BooleanField(default=False)
    comment = models.CharField(max_length=50, blank=True)

    #color = ColorField(default='#FF0000', choices=COLOR_CHOICES)
    color = models.CharField(max_length=7, default='#FF0000', blank=True)

    @property
    def name_com(self):
        return "{}: {}".format(self.name,
                               self.comment)

    @property
    def name_gender(self):
        return "{}: {}".format(self.name,
                               self.tournament_event.category,
                               self.comment)

    def __unicode__(self):
        return "{} {} {}".format(self.tournament_state,
                                 self.name,
                                 self.comment)

    def __str__(self):
        return "{} {}: {} {}".format(self.tournament_event.category,
                                     self.tournament_state,
                                     self.name,
                                     self.comment)

    def get_team_transitions(self):
        ttt = TournamentTeamTransition.objects.filter(origin_ts_id=self).order_by('origin_rank')
        data = {}
        for t in ttt:
            data[t.origin_rank] = t
        return data

    class Meta:
        # managed = False
        db_table = 'bh_tournament_states'

class TournamentTeamTransition(models.Model):
    """ Defines the transistion from a TournamentState to the next.

    Example: origin_rank=1 origin_ts_id=GroupA target_rank=2 otarget_ts_id=QuarterFinal1
    Means that the team who will finish the GroupA on first rank will play 
    QuarterFinal1 on second postion.

    With this a tournament organizer can define the structure of the tournament.
    """
    created_at = UnixDateTimeField(editable=False, default=timezone.now)

    tournament_event = models.ForeignKey('TournamentEvent', null=True, related_name='+', on_delete=models.CASCADE)
    origin_ts_id = models.ForeignKey('TournamentState', null=True, related_name='ttt_origin', on_delete=models.CASCADE)
    origin_rank = models.SmallIntegerField(default=0)
    target_ts_id = models.ForeignKey('TournamentState', null=True, related_name='ttt_target', on_delete=models.CASCADE)
    target_rank = models.SmallIntegerField(default=0)
    keep_stats = models.BooleanField(default=False)
    is_executed = models.BooleanField(default=False)
    comment = models.CharField( max_length=50)

    def __unicode__(self):
        return "Rank {} from {} goes to {}".format(self.origin_rank, self.origin_ts_id,
                                                   self.target_ts_id)

    def __str__(self):
        try:
            data = "Rank {} from {} goes to {}".format(self.origin_rank, self.origin_ts_id.name_com,
                                                   self.target_ts_id.name_com)
        except:
            data = "Rank: {} State: {}".format(self.origin_rank, self.origin_ts_id)
        finally:
            return data

    @classmethod
    def create(cls, tournament, org_rank, org_ts, tar_rank, keepstats, com):
        ttt = cls(tournament=tournament,
                  origin_rank=org_rank,
                  origin_ts_id=org_ts,
                  target_rank=tar_rank,
                  keep_stats=keepstats,
                  comment=com)
        # do something with the book
        return ttt

    class Meta:
        # managed = False
        db_table = 'bh_tournament_team_transition'
        ordering = ['origin_rank']


class TournamentFinalRanking(models.Model):
    """ obsolete because of use of TeamTournamentResult
    """
    series = models.ForeignKey('Series', null=True, related_name='+', on_delete=models.CASCADE)
    tournament_event = models.ForeignKey('TournamentEvent', null=True, related_name='+', on_delete=models.CASCADE)
    rank = models.SmallIntegerField(default=0)
    points = models.SmallIntegerField(default=0)

    def __str__(self):
        return "{} {}: {} {}".format(self.series,
                                     self.tournament_event.name_short,
                                     self.rank,
                                     self.points)

    class Meta:
        db_table = 'bh_tournament_final_ranking'


class TournamentStateRanking(models.Model):
    """ Not used yet
    """
    ts = models.ForeignKey(TournamentState, null=True, related_name='+', on_delete=models.CASCADE)
    next_ts = models.ForeignKey(TournamentState, null=True, on_delete=models.CASCADE)
    rank = models.SmallIntegerField(db_column='rank', default=0)

    def __unicode__(self):
        return self.ts.tournament_state

    class Meta:
        # managed = False
        db_table = 'bh_ts_ranking'


class TournamentStateSorting(models.Model):
    """ This class is for defining the rules, how to rank a 
    tournament state. 

    Not used yet...
    """
    SORTING_CHOICES = (
        ('sets_win', 'sets_win'),
        ('sets_loose', 'sets_loose'),
    )
    tournament_state = models.ForeignKey('TournamentState', null=True, on_delete=models.CASCADE)
    sorting = models.CharField(max_length=13, choices=SORTING_CHOICES)
    priority = models.SmallIntegerField(db_column='priority', default=0)
    comment = models.CharField(max_length=50)

    def __unicode__(self):
        return self.tournament_state.tournament_state

    class Meta:
        db_table = 'bh_ts_sorting'


class Referee(models.Model):
    """ Model for representing a referee.
    """
    created_at = UnixDateTimeField(editable=False, default=timezone.now)

    #user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)

    tournament = models.ForeignKey('Tournament', null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    abbreviation = models.CharField(max_length=12, blank=True, null=True)

    partner = models.ForeignKey("Referee", blank=True, null=True, on_delete=models.SET_NULL)

    gbo_subject_id = models.SmallIntegerField(default=0)


    
    def __unicode__(self):
        return '{} {} ({})'.format(self.first_name, self.name, self.id)

    def __str__(self):
        return '{} {} ({})'.format(self.first_name, self.name, self.id)

    class Meta:
        db_table = 'bh_referee'
        