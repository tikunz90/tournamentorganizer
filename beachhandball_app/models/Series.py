from django.db import models
from django.utils import timezone
from datetime import datetime

from django_unixdatetimefield import UnixDateTimeField

class Series(models.Model):
    """A series represents the highest instance of organization of
    a beachhandball tour.

    The series is the framework for playing a beachhandball season. It defines
    reglementations, accepts tournaments, defines tournaments criterias.
    In the reglementations are the rules for ranking teams and tournaments.

    In Germany the series is called German Beach Open (GBO). In europe it is
    the Eurohandball BeachTour (EBT).

    """
    created_at = UnixDateTimeField(editable=False, default=timezone.now)

    name = models.CharField(max_length=50)
    name_short = models.CharField(max_length=50)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        db_table = 'bh_series'


class Season(models.Model):
    """A season defines the time period for which beachhandball is played.

    Typical time frame is one year. So all collected TeamTournamentResults
    within this season will be considered for the series ranking.

    """
    created_at = UnixDateTimeField(editable=False, default=timezone.now)

    name = models.CharField(max_length=50)
    start_ts = UnixDateTimeField(null=False, default=timezone.now)
    end_ts = UnixDateTimeField(null=False, default=timezone.now)

    is_actual = models.BooleanField(default=False)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        # managed = False
        db_table = 'bh_season'

class SeriesTournamentRegistration(models.Model):
    """A season defines the time period for which beachhandball is played.

    Typical time frame is one year. So all collected TeamTournamentResults
    within this season will be considered for the series ranking.

    """
    created_at = UnixDateTimeField(editable=False, default=timezone.now)

    season = models.ForeignKey('Season', null=True, related_name='+', on_delete=models.SET_NULL)
    series = models.ForeignKey('Series', null=True, related_name='+', on_delete=models.SET_NULL)
    tournament = models.ForeignKey('Tournament', null=True, related_name='+', on_delete=models.SET_NULL)
    series_cup = models.ForeignKey('SeriesCup', null=True, related_name='+', on_delete=models.SET_NULL)

    def __str__(self):
        return "STR: Season {}: {} - {} - {}".format(self.season, self.series, self.tournament, self.series_cup)

    class Meta:
        db_table = 'bh_series_tournament_reg'


class SeriesCup(models.Model):
    """The SeriesCup defines the category for a tournament and value of the tournament.

    Possibilities for GBO are Super-Cup, Beach-Cup, 4Fun-Cup

    """
    created_at = UnixDateTimeField(editable=False, default=timezone.now)

    season = models.ForeignKey('Season', null=True, related_name='+', on_delete=models.CASCADE)
    series = models.ForeignKey('Series', null=True, related_name='+', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    order = models.SmallIntegerField(default=0)

    def __unicode__(self):
        return '{}'.format(self.name)

    def __str__(self):
        return '{}'.format(self.name)

    class Meta:
        db_table = 'bh_series_cup'


class SeriesCupCriteria(models.Model):
    """The SeriesCupCriteria defines criterias for define value of a tournament.

    Possibilities for GBO are Super-Cup, Beach-Cup, 4Fun-Cup

    """
    created_at = UnixDateTimeField(editable=False, default=timezone.now)

    season = models.ForeignKey('Season', null=True, related_name='+', on_delete=models.CASCADE)
    series = models.ForeignKey('Series', null=True, related_name='+', on_delete=models.CASCADE)
    cup = models.ForeignKey('SeriesCup', null=True, related_name='+', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    points = models.SmallIntegerField(default=-1)
    max_points = models.SmallIntegerField(default=-1)
    is_required = models.BooleanField(null=True, default=False)

    is_active = models.BooleanField(null=True, default=False)
    is_confirmed = models.BooleanField(null=True, default=False)
    

    class Meta:
        db_table = 'bh_series_cup_criteria'