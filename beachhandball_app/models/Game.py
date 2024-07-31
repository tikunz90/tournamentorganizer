from django.db import models
from django.utils import timezone
from datetime import datetime

from django_unixdatetimefield import UnixDateTimeField
import jsonfield

from .choices import COURT_CHOICES, GAMESTATE_CHOICES, GAMESTATE_SCOUTING_CHOICES

class GameManager(models.Manager):

    def get_queryset(self):
        qs = super().get_queryset()
        return qs
        return qs.select_related('tournament', 'tournament_event__category','tournament_state', 'team_a', 'team_b', 'team_st_a__team', 'team_st_b__team', 'ref_a', 'ref_b', 'court')

    def appending(self, tourn_id):
        qs = super().get_queryset()
        return qs.select_related('tournament', 'tournament_event__category','tournament_state', 'team_a', 'team_b', 'team_st_a__team', 'team_st_b__team', 'ref_a', 'ref_b', 'court') #.filter(tournament=tourn_id, gamestate='APPENDING')


class Game(models.Model):
    """ Model for representing a beachhandball game.
    """
    #objects = GameManager()

    created_at = UnixDateTimeField(editable=False, default=timezone.now)

    GAMINGSTATE_CHOICES = (
        ('Ready', 'Ready',),
        ('1.HT', '1.HT', ),
        ('Halftime Break', 'Halftime Break',),
        ('2.HT', '2.HT'),
        ('Penalty', 'Penalty',),
        ('Paused', 'Paused',),
        ('Finished', 'Finished'),
        ('SignRequired', 'SignRequired',),
    )

    tournament = models.ForeignKey('Tournament', null=True, on_delete=models.CASCADE)
    tournament_event = models.ForeignKey('TournamentEvent', null=True, on_delete=models.CASCADE)
    team_a = models.ForeignKey('Team',related_name='TeamA', null=True, blank=True, on_delete=models.SET_NULL)
    team_b = models.ForeignKey('Team',related_name='TeamB', null=True, blank=True, on_delete=models.SET_NULL)
    team_st_a = models.ForeignKey('TeamStats', null=True, related_name='+', on_delete=models.CASCADE)
    team_st_b = models.ForeignKey('TeamStats', null=True, related_name='+', on_delete=models.CASCADE)
    tournament_state = models.ForeignKey('TournamentState', blank=True, null=True, on_delete=models.CASCADE)
    ref_a = models.ForeignKey('Referee',related_name='RefA', null=True, blank=True, on_delete=models.SET_NULL)
    ref_b = models.ForeignKey('Referee',related_name='RefB', null=True, blank=True, on_delete=models.SET_NULL)
    starttime = UnixDateTimeField(db_column='start_ts', default=timezone.now)
    duration_of_halftime = models.IntegerField(default=600)
    number_of_penalty_tries = models.SmallIntegerField(default=5)
    court = models.ForeignKey('Court', blank=True, null=True, on_delete=models.SET_NULL)
    score_team_a_halftime_1 = models.SmallIntegerField(default=0, blank=True, null=True)
    score_team_a_halftime_2 = models.SmallIntegerField(default=0, blank=True, null=True)
    score_team_a_penalty = models.SmallIntegerField(default=0, blank=True, null=True)
    score_team_b_halftime_1 = models.SmallIntegerField(default=0, blank=True, null=True)
    score_team_b_halftime_2 = models.SmallIntegerField(default=0, blank=True, null=True)
    score_team_b_penalty = models.SmallIntegerField(default=0, blank=True, null=True)
    setpoints_team_a = models.SmallIntegerField(default=0, blank=True, null=True)
    setpoints_team_b = models.SmallIntegerField(default=0, blank=True, null=True)
    winner_halftime_1 = models.IntegerField(blank=True, null=True)
    winner_halftime_2 = models.IntegerField(blank=True, null=True)
    winner_penalty = models.IntegerField( blank=True, null=True)
    winner = models.IntegerField( blank=True, null=True)
    gamestate = models.CharField(max_length=9, blank=True, null=True, choices=GAMESTATE_CHOICES)
    act_time = models.IntegerField(blank=True, null=True)
    gamingstate = models.CharField(
        max_length=14,
        blank=True,
        null=True,
        choices=GAMINGSTATE_CHOICES
    )
    scouting_state = models.CharField(max_length=9, blank=True, null=True, choices=GAMESTATE_SCOUTING_CHOICES)
    id_counter = models.IntegerField(default=0, blank=True, null=True)

    last_real_time_data = jsonfield.JSONField(null=True, blank=True)
    gbo_ref_a_subject_id = models.SmallIntegerField(default=0, blank=True, null=True)
    gbo_ref_b_subject_id = models.SmallIntegerField(default=0, blank=True, null=True)

    def __unicode__(self):
        return '{}: {} - {} um {}'.format(self.tournament_state, self.team_st_a, self.team_st_b, self.starttime)

    def __str__(self):
        return '{}: {} - {} um {}'.format(self.tournament_state, self.team_st_a, self.team_st_b, self.starttime)

    def calc_winner(self):
        try:
            if self.gamestate == 'FINISHED':
                sc_ta_ht1 = self.score_team_a_halftime_1
                sc_tb_ht1 = self.score_team_b_halftime_1
                sc_ta_ht2 = self.score_team_a_halftime_2
                sc_tb_ht2 = self.score_team_b_halftime_2
                sc_ta_htp = self.score_team_a_penalty
                sc_tb_htp = self.score_team_b_penalty
                self.setpoints_team_a = 0
                self.setpoints_team_b = 0
                self.winner_halftime_1 = 0
                self.winner_halftime_2 = 0
                self.winner_penalty = 0
                self.winner = -1
                if sc_ta_ht1 > sc_tb_ht1:
                    self.winner_halftime_1 = self.team_st_a.id
                    self.winner = self.team_st_a.id
                    self.setpoints_team_a = self.setpoints_team_a + 1
                else:
                    self.winner_halftime_1 = self.team_st_b.id
                    self.winner = self.team_st_b.id
                    self.setpoints_team_b = self.setpoints_team_b + 1
                if sc_ta_ht2 > sc_tb_ht2:
                    self.winner_halftime_2 = self.team_st_a.id
                    self.winner = self.team_st_a.id
                    self.setpoints_team_a = self.setpoints_team_a + 1
                else:
                    self.winner_halftime_2 = self.team_st_b.id
                    self.winner = self.team_st_b.id
                    self.setpoints_team_b = self.setpoints_team_b + 1
                if self.winner_halftime_1 is not self.winner_halftime_2:
                    if sc_ta_htp > sc_tb_htp:
                        self.winner_penalty = self.team_st_a.id
                        self.winner = self.team_st_a.id
                        self.setpoints_team_a = self.setpoints_team_a + 1
                    else:
                        self.winner_penalty = self.team_st_b.id
                        self.winner = self.team_st_b.id
                        self.setpoints_team_b = self.setpoints_team_b + 1
        except Exception as ex:
            return ex
        finally:
            return True

    class Meta:
        db_table = 'bh_game'
        ordering = ['starttime']


class GameAction(models.Model):
    """ Model for representing actions in a game.

    While a running game scouts are tracking all actions happening in a game.
    This creates the history report of the game and player statistics.
    """
    created_at = UnixDateTimeField(editable=False, default=timezone.now)

    PERIOD_CHOICES = (
        ('HT1', 'HT1'),
        ('HT2', 'HT2'),
        ('P', 'P'),
    )

    ACTION_CHOICES = (
        ('KEMPA', 'KEMPA'),
        ('SPIN', 'SPIN'),
        ('SHOOTER', 'SHOOTER'),
        ('ONE', 'ONE'),
        ('BLOCK', 'BLOCK'),
        ('STEAL', 'STEAL'),
        ('ASSIST', 'ASSIST'),
        ('TURNOVER', 'TURNOVER'),
        ('GK_SAVE', 'GK_SAVE'),
        ('SUSPENSION', 'SUSPENSION'),
        ('REDCARD', 'REDCARD'),
        ('CORRECTION', 'CORRECTION'),
        ('SixM', 'SixM'),
        ('TEAM_TIMEOUT', 'TEAM_TIMEOUT'),
    )

    tournament = models.ForeignKey('Tournament', null=True, related_name='+', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(db_column='TimeStamp', auto_now_add=True)
    gametime = models.TimeField(db_column='GameTime', default='00:00:00')
    period = models.CharField(db_column='Period', max_length=3, choices=PERIOD_CHOICES)
    game = models.ForeignKey(Game, null=True, on_delete=models.CASCADE)
    player = models.ForeignKey('Player', null=True, on_delete=models.CASCADE)
    team = models.ForeignKey('Team', null=True, on_delete=models.CASCADE)
    action = models.CharField(db_column='Action', max_length=10, choices=ACTION_CHOICES)
    action_result = models.CharField(db_column='ActionResult', max_length=7)
    score_team_a = models.SmallIntegerField(default=0, blank=True, null=True)
    score_team_b = models.SmallIntegerField(default=0, blank=True, null=True)
    time_min = models.SmallIntegerField(default=0, blank=True, null=True)
    time_sec = models.SmallIntegerField(default=0, blank=True, null=True)
    guid = models.CharField(null=True, blank=True, max_length=32)
    active_defending_gk_id = models.IntegerField(default=0, blank=True, null=True)

    def __unicode__(self):
        return 'Gameaction ID: {}'.format(self.id)

    def __str__(self):
        return 'Gameaction ID: {}'.format(self.id)

    class Meta:
        db_table = 'bh_gameaction'


class ScoutingReport(models.Model):
    """ Link between game and scouting report
    """
    created_at = UnixDateTimeField(editable=False, default=timezone.now)

    tournament_event = models.ForeignKey('TournamentEvent', null=True, on_delete=models.CASCADE)
    game = models.ForeignKey('Game', null=True, on_delete=models.CASCADE)
    scouter = models.ForeignKey('Scouter', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return "({}) ScoutingReport: {}".format(self.id,
                                     self.game)

    class Meta:
        db_table = 'bh_game_scouting_report'