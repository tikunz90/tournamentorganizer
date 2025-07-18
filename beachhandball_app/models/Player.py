from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import datetime

from django_unixdatetimefield import UnixDateTimeField
import jsonfield

class Player(models.Model):
    """ Model for representing a player of a team.
    """  
    created_at = UnixDateTimeField(editable=False, default=timezone.now)

    #user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)

    tournament_event = models.ForeignKey('TournamentEvent', null=True, on_delete=models.CASCADE)
    team = models.ForeignKey('Team', null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    number = models.SmallIntegerField(null=True)
    birthday = models.DateField(blank=True, null=True)

    position = models.ForeignKey('PlayerPosition', null=True, on_delete=models.SET_NULL)

    is_active = models.BooleanField(null=True, default=False)

    season_team_id = models.IntegerField(null=True)
    season_player_id = models.IntegerField(null=True)
    gbo_position = models.CharField(max_length=50, blank=True, null=True)
    subject_data = jsonfield.JSONField(null=True)
    
    
    def __unicode__(self):
        return '{} {} ({})'.format(self.first_name, self.name, self.id)

    def __str__(self):
        return '{} {} ({})'.format(self.first_name, self.name, self.id)

    class Meta:
        db_table = 'bh_player'

class PlayerStatsManager(models.Manager):

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related('tournament_event', 'game','player', 'teamstat')

class PlayerStats(models.Model):
    """ PlayerStats is created for each player for each game.

    This object will feeded with statistics while game is running.
    """
    objects = PlayerStatsManager()

    created_at = UnixDateTimeField(editable=False, default=timezone.now)

    tournament_event = models.ForeignKey('TournamentEvent', null=True, on_delete=models.CASCADE)
    game = models.ForeignKey('Game', blank=True, null=True, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, blank=True, null=True, on_delete=models.CASCADE)
    teamstat = models.ForeignKey('TeamStats', null=True, on_delete=models.CASCADE)
    score = models.SmallIntegerField(blank=True, default=0)
    kempa_try = models.SmallIntegerField(blank=True, default=0)
    kempa_success = models.SmallIntegerField(blank=True, default=0)
    spin_try = models.SmallIntegerField(blank=True, default=0)
    spin_success = models.SmallIntegerField(blank=True, default=0)
    shooter_try = models.SmallIntegerField(blank=True, default=0)
    shooter_success = models.SmallIntegerField(blank=True, default=0)
    sixm_try = models.SmallIntegerField(blank=True, default=0)
    sixm_success = models.SmallIntegerField(blank=True, default=0)
    one_try = models.SmallIntegerField(blank=True, default=0)
    one_success = models.SmallIntegerField(blank=True, default=0)
    suspension = models.SmallIntegerField(blank=True, default=0)
    redcard = models.SmallIntegerField(blank=True, default=0)
    is_ranked = models.BooleanField(blank=True, default=False)
    games_played = models.SmallIntegerField(blank=True, default=False)
    goal_keeper_success = models.SmallIntegerField(blank=True, default=0)
    shots_on_goal = models.SmallIntegerField(blank=True, default=0)

    block_success = models.SmallIntegerField(blank=True, default=0)
    steal_success = models.SmallIntegerField(blank=True, default=0)
    turnover_success = models.SmallIntegerField(blank=True, default=0)
    assist_success = models.SmallIntegerField(blank=True, default=0)

    mvp_score = models.FloatField(null=True, blank=True, default=0)
    mvp_offense_score = models.FloatField(null=True, blank=True, default=0)
    mvp_defense_score = models.FloatField(null=True, blank=True, default=0)
    mvp_goalie_score = models.FloatField(null=True, blank=True, default=0)

    season_team_id = models.IntegerField(null=True)
    season_player_id = models.IntegerField(null=True)
    season_cup_tournament_id = models.IntegerField(null=True, default=0)
    season_cup_german_championship_id = models.IntegerField(null=True, default=0)

    gbo_category_id = models.IntegerField(default=0)
    
    @staticmethod
    def calc_score(ps):
        score = 0
        score += ps.one_success
        score += ps.kempa_success * 2
        score += ps.shooter_success * 2
        score += ps.spin_success * 2
        score += ps.sixm_success * 2
        return score

    def __unicode__(self):
        return '{} {} ({})'.format(self.player.first_name, self.player.name, self.id)

    def __str__(self):
        return '#{} {} {} ({})'.format(self.player.number, self.player.first_name, self.player.name, self.id)

    class Meta:
        db_table = 'bh_player_game_stats'


class PlayerPosition(models.Model):
    """ Model for representing a player position like defender, offense, goalkeeper
    """
    created_at = UnixDateTimeField(editable=False, default=timezone.now)

    name = models.CharField(max_length=50)
    name_short = models.CharField(max_length=2)

    
    def __unicode__(self):
        return '{} ({})'.format(self.name, self.name_short)

    def __str__(self):
        return '{} ({})'.format(self.name, self.name_short)

    class Meta:
        db_table = 'bh_player_position'