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
        ('man', 'man'),
        ('men', 'men'),
        ('woman', 'woman'),
        ('women', 'women'),
        ('U14', 'U14'),
        ('U15', 'U15'),
        ('U16', 'U16'),
        ('U17', 'U17'),
        ('U18', 'U18'),
        ('U19', 'U19'),
        ('U20', 'U20'),
        ('U21', 'U21'),

    )


class TournamentCategory(models.Model):
    """ Model representing a tournament category like MEN, WOMEN, JUNIOR.
    """
    created_at = UnixDateTimeField(editable=False, default=timezone.now)

    name = models.CharField(db_column='name', max_length=50)
    abbreviation = models.CharField(max_length=3, blank=True)
    classification = models.CharField(max_length=50, choices=CATEGORY_CLASS_CHOICES, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, blank=True)

    gbo_category_id = models.IntegerField(default=0)
    season_tournament_category_id = models.IntegerField(null=True, blank=True)
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


class GameReportTemplate(models.Model):
    """ Model representing a templatefile for the gamereport
    """
    created_at = UnixDateTimeField(editable=False, default=timezone.now)

    filename = models.CharField(db_column='filename', max_length=127)

    max_num_player = models.SmallIntegerField(default=10)
    max_num_coaches = models.SmallIntegerField(default=2)

    cell_game_id = models.CharField(max_length=6, default='T4')
    
    cell_category_men = models.CharField(max_length=6, default='M3')
    cell_category_women = models.CharField(max_length=6, default='P3')
    
    cell_court_number = models.CharField(max_length=6, default='R8')

    cell_team_a_name = models.CharField(max_length=6, default='B8')
    cell_team_b_name = models.CharField(max_length=50, default='G8')

    cell_ref_a_name = models.CharField(max_length=6, default='B48')
    cell_ref_b_name = models.CharField(max_length=6, default='B49')

    cell_group_stage = models.CharField(max_length=6, default='I4')
    cell_knockout_stage = models.CharField(max_length=6, default='I5')

    cell_date = models.CharField(max_length=6, default='C10')
    cell_time = models.CharField(max_length=6, default='F10')

    team_a_start_row = models.SmallIntegerField(default=13)
    team_a_player_number_col = models.CharField(max_length=6, default='A')
    team_a_player_name_col = models.CharField(max_length=6, default='B')
    team_a_start_row_coaches = models.SmallIntegerField(default=25)
    team_a_coach_name_col = models.CharField(max_length=6, default='B')

    team_b_start_row = models.SmallIntegerField(default=30)
    team_b_player_number_col = models.CharField(max_length=6, default='A')
    team_b_player_name_col = models.CharField(max_length=6, default='B')
    team_b_start_row_coaches = models.SmallIntegerField(default=42)
    team_b_coach_name_col = models.CharField(max_length=6, default='B')

    def __unicode__(self):
        return self.filename

    def __str__(self):
        return self.filename
    class Meta:
        db_table = 'bh_game_report_template'