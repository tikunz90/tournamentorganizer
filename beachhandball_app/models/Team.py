from django.db import models
from django.utils import timezone
from datetime import datetime

from django_unixdatetimefield import UnixDateTimeField

from .choices import NATIONALITY_CHOICES, TEAM_TOURNAMENT_REG


class Team(models.Model):
    """ Model representing a Team.
    """
    created_at = UnixDateTimeField(editable=False, default=timezone.now)

    tournament_event = models.ForeignKey('TournamentEvent', blank=True, null=True, on_delete=models.CASCADE)
    tournamentstate = models.ForeignKey('TournamentState', blank=True, null=True, on_delete=models.CASCADE)
    name = models.CharField(db_column='name', max_length=50)
    abbreviation = models.CharField(max_length=8, null=True)
    gbo_team = models.IntegerField(null=True)
    season_team_id = models.IntegerField(null=True)
    season_team_cup_tournament_ranking_id = models.IntegerField(null=True)
    status_progress = models.CharField(max_length=25, null=True)
    
    category = models.ForeignKey('TournamentCategory', null=True, related_name='+', on_delete=models.CASCADE)
    is_dummy = models.BooleanField(null=True, default=False)

    def __unicode__(self):
        return '({}) {}'.format(self.id, self.name)

    def __str__(self):
        return '({}) {}'.format(self.id, self.name)

    class Meta:
        # managed = False
        db_table = 'bh_team'


class TeamStats(models.Model):
    """ TeamStats are holding the results of a team within one TournamentState.

    For example TeamA plays games in GroupA. There will be one TeamStats object created.
    All gameresults from this team will be applied to the TeamStat. TeamStats are then used to
    rank the TournamentState.

    After all games are played in a TournamentState. Teams will transit to the next state and get a new 
    TeamStats object.

    """
    created_at = UnixDateTimeField(editable=False, default=timezone.now)

    tournament_event = models.ForeignKey('TournamentEvent', null=True, related_name='+', on_delete=models.CASCADE)
    team = models.ForeignKey(Team, null=True, on_delete=models.CASCADE, blank=True)
    tournamentstate = models.ForeignKey('TournamentState', null=True, on_delete=models.CASCADE)
    number_of_played_games = models.SmallIntegerField(blank=True, null=True, default=0)
    game_points = models.SmallIntegerField(blank=True, null=True, default=0)
    game_points_bonus = models.SmallIntegerField(blank=True, null=True, default=0)
    ranking_points = models.SmallIntegerField(blank=True, null=True, default=0)
    sets_win = models.SmallIntegerField( blank=True, null=True, default=0)
    sets_loose = models.SmallIntegerField(blank=True, null=True, default=0)
    points_made = models.SmallIntegerField(blank=True, null=True, default=0)
    points_received = models.SmallIntegerField( blank=True, null=True, default=0)
    rank_initial = models.SmallIntegerField(blank=True, null=True, default=0)
    rank = models.SmallIntegerField(blank=True, null=True, default=0)
    name_table = models.CharField(db_column='name_table', max_length=50, null=True, default='No team')

    @property
    def stats(self):
        return "{} {}:{} {}:{} {} {} ".format(self.number_of_played_games,
                                              self.sets_win,
                                              self.sets_loose,
                                              self.points_made,
                                              self.points_received,
                                              self.game_points,
                                              self.game_points_bonus)

    def __unicode__(self):
        if self.team is None:
            name = 'No team'
        else:
            name = self.team.name
        return "{}: ({}) {} {}:{} {}:{} ".format(name,
                                                 self.tournamentstate.tournament_state,
                                                 self.number_of_played_games,
                                                 self.sets_win,
                                                 self.sets_loose,
                                                 self.points_made,
                                                 self.points_received)

    def __str__(self):
        if self.team is None:
            name = self.name_table
        else:
            name = self.team.name
        return name

    @classmethod
    def create(cls, tournament, tournament_state, init_rnk):
        teamstat = cls(tournament=tournament, tournamentstate=tournament_state, rank_initial=init_rnk)
        return teamstat

    class Meta:
        # managed = False
        db_table = 'bh_team_stats'
        ordering = ['-ranking_points']


class TeamTournamentResult(models.Model):
    """TeamTournamentResult (TTR) defines the final result of a 
    team who played the specified tournament in a season.

    The rank defines the final placement reached on this tournament and
    points are the received amount of points for this placement. The amount
    is specified by the value of the played tournament.
    """
    created_at = UnixDateTimeField(editable=False, default=timezone.now)

    season = models.ForeignKey('Season', null=True, related_name='+', on_delete=models.CASCADE)
    series = models.ForeignKey('Series', null=True, related_name='+', on_delete=models.CASCADE)
    tournament_event = models.ForeignKey('TournamentEvent', null=True, related_name='+', on_delete=models.CASCADE)
    team = models.ForeignKey('Team', null=True, related_name='+', on_delete=models.CASCADE)

    rank = models.SmallIntegerField(default=0)
    points = models.SmallIntegerField(default=0)

    class Meta:
        db_table = 'bh_team_tourn_result'


class TeamTournamentRegistration(models.Model):
    """TeamTournamentRegistration defines a registration request of
    a team to a tournamentevent.

    Request has to be accepted by TO.
    """
    created_at = UnixDateTimeField(editable=False, default=timezone.now)

    season = models.ForeignKey('Season', null=True, related_name='+', on_delete=models.CASCADE)
    series = models.ForeignKey('Series', null=True, related_name='+', on_delete=models.CASCADE)
    tournament_event = models.ForeignKey('TournamentEvent', null=True, related_name='+', on_delete=models.CASCADE)
    team = models.ForeignKey('Team', null=True, related_name='+', on_delete=models.CASCADE)

    registration_state = models.CharField(db_column='registration_state', max_length=50,
                                   choices=TEAM_TOURNAMENT_REG, default=TEAM_TOURNAMENT_REG[0])

    def __str__(self):
        return '{} {}'.format(self.team.name, self.registration_state)

    class Meta:
        db_table = 'bh_team_tournanment_registration'


class Coach(models.Model):
    """ Model for representing a player of a team.
    """
    created_at = UnixDateTimeField(editable=False, default=timezone.now)

    #user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)

    tournament_event = models.ForeignKey('TournamentEvent', null=True, on_delete=models.CASCADE)
    team = models.ForeignKey('Team', null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)

    season_team_id = models.IntegerField(null=True)
    season_coach_id = models.IntegerField(null=True)
    gbo_position = models.CharField(max_length=50, blank=True, null=True)
    
    
    def __unicode__(self):
        return '{} {} ({})'.format(self.first_name, self.name, self.id)

    def __str__(self):
        return '{} {} ({})'.format(self.first_name, self.name, self.id)

    class Meta:
        db_table = 'bh_coach'