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
    gbo_season_id = models.SmallIntegerField(default=0)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        # managed = False
        db_table = 'bh_season'
