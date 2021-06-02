from django.db import models
from django.utils import timezone
from datetime import datetime

from django_unixdatetimefield import UnixDateTimeField

from .choices import NATIONALITY_CHOICES, CATEGORY_CHOICES

CATEGORY_CLASS_CHOICES = (
        ('Adult', 'Adult'),
        ('Seniors', 'Seniors'),
        ('Junior', 'Junior'),
        ('Mixed', 'Mixed'),
    )


class TournamentCategory(models.Model):
    """ Model representing a tournament category like MEN, WOMEN, JUNIOR.
    """
    created_at = UnixDateTimeField(editable=False, default=timezone.now)

    name = models.CharField(db_column='name', max_length=50)
    abbreviation = models.CharField(max_length=3, blank=True)
    classification = models.CharField(max_length=50, choices=CATEGORY_CLASS_CHOICES, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, blank=True)

    gbo_category_id = models.IntegerField(null=True)
    season_tournament_category_id = models.IntegerField(null=True)
    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    @property
    def icon(self):
        if self.category == CATEGORY_CHOICES[0][0]:
            return 'male'
        elif self.category == CATEGORY_CHOICES[1][0]:
            return 'female'
        else:
            return 'group'


    class Meta:
        db_table = 'bh_tourn_category'