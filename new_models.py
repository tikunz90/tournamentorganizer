# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class AuthenticationGbouser(models.Model):
    gbo_user = models.CharField(max_length=100)
    token = models.TextField()
    validuntil = models.PositiveIntegerField(db_column='validUntil')  # Field name made lowercase.
    subject_id = models.IntegerField(blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING, unique=True)
    is_online = models.IntegerField()
    gbo_data = models.TextField()

    class Meta:
        managed = False
        db_table = 'authentication_gbouser'


class BhCourts(models.Model):
    created_at = models.PositiveIntegerField()
    name = models.CharField(max_length=50)
    number = models.SmallIntegerField()
    tournament = models.ForeignKey('BhTournament', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bh_courts'


class BhGame(models.Model):
    created_at = models.PositiveIntegerField()
    start_ts = models.PositiveIntegerField()
    duration_of_halftime = models.IntegerField()
    number_of_penalty_tries = models.SmallIntegerField()
    score_team_a_halftime_1 = models.SmallIntegerField(blank=True, null=True)
    score_team_a_halftime_2 = models.SmallIntegerField(blank=True, null=True)
    score_team_a_penalty = models.SmallIntegerField(blank=True, null=True)
    score_team_b_halftime_1 = models.SmallIntegerField(blank=True, null=True)
    score_team_b_halftime_2 = models.SmallIntegerField(blank=True, null=True)
    score_team_b_penalty = models.SmallIntegerField(blank=True, null=True)
    winner_halftime_1 = models.IntegerField(blank=True, null=True)
    winner_halftime_2 = models.IntegerField(blank=True, null=True)
    winner_penalty = models.IntegerField(blank=True, null=True)
    gamestate = models.CharField(max_length=9, blank=True, null=True)
    act_time = models.IntegerField(blank=True, null=True)
    gamingstate = models.CharField(max_length=14, blank=True, null=True)
    scouting_state = models.CharField(max_length=9, blank=True, null=True)
    court = models.ForeignKey(BhCourts, models.DO_NOTHING, blank=True, null=True)
    team_st_a = models.ForeignKey('BhTeamStats', models.DO_NOTHING, blank=True, null=True)
    team_st_b = models.ForeignKey('BhTeamStats', models.DO_NOTHING, blank=True, null=True)
    tournament = models.ForeignKey('BhTournament', models.DO_NOTHING, blank=True, null=True)
    tournament_event = models.ForeignKey('BhTournamentEvent', models.DO_NOTHING, blank=True, null=True)
    tournament_state = models.ForeignKey('BhTournamentStates', models.DO_NOTHING, blank=True, null=True)
    winner = models.IntegerField(blank=True, null=True)
    setpoints_team_a = models.SmallIntegerField(blank=True, null=True)
    setpoints_team_b = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bh_game'


class BhGameaction(models.Model):
    created_at = models.PositiveIntegerField()
    timestamp = models.DateTimeField(db_column='TimeStamp')  # Field name made lowercase.
    gametime = models.TimeField(db_column='GameTime')  # Field name made lowercase.
    period = models.CharField(db_column='Period', max_length=3)  # Field name made lowercase.
    action = models.CharField(db_column='Action', max_length=10)  # Field name made lowercase.
    actionresult = models.CharField(db_column='ActionResult', max_length=7)  # Field name made lowercase.
    score_team_a = models.SmallIntegerField(blank=True, null=True)
    score_team_b = models.SmallIntegerField(blank=True, null=True)
    time_min = models.SmallIntegerField(blank=True, null=True)
    time_sec = models.SmallIntegerField(blank=True, null=True)
    game = models.ForeignKey(BhGame, models.DO_NOTHING, blank=True, null=True)
    player = models.ForeignKey('BhPlayer', models.DO_NOTHING, blank=True, null=True)
    team = models.ForeignKey('BhTeam', models.DO_NOTHING, blank=True, null=True)
    tournament = models.ForeignKey('BhTournament', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bh_gameaction'


class BhPlayer(models.Model):
    created_at = models.PositiveIntegerField()
    name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    number = models.SmallIntegerField()
    birthday = models.DateField(blank=True, null=True)
    position = models.ForeignKey('BhPlayerPosition', models.DO_NOTHING, blank=True, null=True)
    team = models.ForeignKey('BhTeam', models.DO_NOTHING, blank=True, null=True)
    tournament_event = models.ForeignKey('BhTournamentEvent', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bh_player'


class BhPlayerGameStats(models.Model):
    created_at = models.PositiveIntegerField()
    score = models.SmallIntegerField()
    kempa_try = models.SmallIntegerField()
    kempa_success = models.SmallIntegerField()
    spin_try = models.SmallIntegerField()
    spin_success = models.SmallIntegerField()
    shooter_try = models.SmallIntegerField()
    shooter_success = models.SmallIntegerField()
    one_try = models.SmallIntegerField()
    one_success = models.SmallIntegerField()
    suspension = models.SmallIntegerField()
    redcard = models.SmallIntegerField()
    is_ranked = models.SmallIntegerField()
    games_played = models.SmallIntegerField()
    goal_keeper_success = models.SmallIntegerField()
    block_success = models.SmallIntegerField()
    game = models.ForeignKey(BhGame, models.DO_NOTHING, blank=True, null=True)
    player = models.ForeignKey(BhPlayer, models.DO_NOTHING, blank=True, null=True)
    teamstat = models.ForeignKey('BhTeamStats', models.DO_NOTHING, blank=True, null=True)
    tournament_event = models.ForeignKey('BhTournamentEvent', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bh_player_game_stats'


class BhPlayerPosition(models.Model):
    created_at = models.PositiveIntegerField()
    name = models.CharField(max_length=50)
    name_short = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'bh_player_position'


class BhReferee(models.Model):
    created_at = models.PositiveIntegerField()
    name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    abbreviation = models.CharField(max_length=12, blank=True, null=True)
    gbo_subject_id = models.SmallIntegerField()
    partner = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)
    tournament = models.ForeignKey('BhTournament', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bh_referee'


class BhSeason(models.Model):
    created_at = models.PositiveIntegerField()
    name = models.CharField(max_length=50)
    start_ts = models.PositiveIntegerField()
    end_ts = models.PositiveIntegerField()
    is_actual = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'bh_season'


class BhSeries(models.Model):
    created_at = models.PositiveIntegerField()
    name = models.CharField(max_length=50)
    name_short = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'bh_series'


class BhTeam(models.Model):
    created_at = models.PositiveIntegerField()
    name = models.CharField(max_length=50)
    abbreviation = models.CharField(max_length=8, blank=True, null=True)
    gbo_team = models.IntegerField(blank=True, null=True)
    is_dummy = models.IntegerField(blank=True, null=True)
    category = models.ForeignKey('BhTournCategory', models.DO_NOTHING, blank=True, null=True)
    tournament_event = models.ForeignKey('BhTournamentEvent', models.DO_NOTHING, blank=True, null=True)
    tournamentstate = models.ForeignKey('BhTournamentStates', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bh_team'


class BhTeamStats(models.Model):
    created_at = models.PositiveIntegerField()
    number_of_played_games = models.SmallIntegerField(blank=True, null=True)
    game_points = models.SmallIntegerField(blank=True, null=True)
    game_points_bonus = models.SmallIntegerField(blank=True, null=True)
    ranking_points = models.SmallIntegerField(blank=True, null=True)
    sets_win = models.SmallIntegerField(blank=True, null=True)
    sets_loose = models.SmallIntegerField(blank=True, null=True)
    points_made = models.SmallIntegerField(blank=True, null=True)
    points_received = models.SmallIntegerField(blank=True, null=True)
    rank_initial = models.SmallIntegerField(blank=True, null=True)
    rank = models.SmallIntegerField(blank=True, null=True)
    name_table = models.CharField(max_length=50, blank=True, null=True)
    team = models.ForeignKey(BhTeam, models.DO_NOTHING, blank=True, null=True)
    tournament_event = models.ForeignKey('BhTournamentEvent', models.DO_NOTHING, blank=True, null=True)
    tournamentstate = models.ForeignKey('BhTournamentStates', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bh_team_stats'


class BhTeamTournResult(models.Model):
    created_at = models.PositiveIntegerField()
    rank = models.SmallIntegerField()
    points = models.SmallIntegerField()
    season = models.ForeignKey(BhSeason, models.DO_NOTHING, blank=True, null=True)
    series = models.ForeignKey(BhSeries, models.DO_NOTHING, blank=True, null=True)
    team = models.ForeignKey(BhTeam, models.DO_NOTHING, blank=True, null=True)
    tournament_event = models.ForeignKey('BhTournamentEvent', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bh_team_tourn_result'


class BhTeamTournanmentRegistration(models.Model):
    created_at = models.PositiveIntegerField()
    registration_state = models.CharField(max_length=50)
    season = models.ForeignKey(BhSeason, models.DO_NOTHING, blank=True, null=True)
    series = models.ForeignKey(BhSeries, models.DO_NOTHING, blank=True, null=True)
    team = models.ForeignKey(BhTeam, models.DO_NOTHING, blank=True, null=True)
    tournament_event = models.ForeignKey('BhTournamentEvent', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bh_team_tournanment_registration'


class BhTournCategory(models.Model):
    created_at = models.PositiveIntegerField()
    name = models.CharField(max_length=50)
    abbreviation = models.CharField(max_length=3)
    classification = models.CharField(max_length=50)
    category = models.CharField(max_length=50)
    season_tournament_category_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bh_tourn_category'


class BhTournament(models.Model):
    created_at = models.PositiveIntegerField()
    organizer = models.SmallIntegerField()
    name = models.CharField(max_length=50)
    gbo_data = models.TextField()
    gbo_season_cup_tournament = models.ForeignKey('SeasonCupTournament', models.DO_NOTHING)
    is_active = models.IntegerField()
    last_sync_at = models.PositiveIntegerField()
    gbo_season_tournament_id = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'bh_tournament'


class BhTournamentEvent(models.Model):
    created_at = models.PositiveIntegerField()
    name = models.CharField(max_length=50)
    start_ts = models.PositiveIntegerField()
    end_ts = models.PositiveIntegerField()
    max_number_teams = models.SmallIntegerField()
    is_in_configuration = models.IntegerField()
    season_tournament_id = models.IntegerField(blank=True, null=True)
    category = models.ForeignKey(BhTournCategory, models.DO_NOTHING, blank=True, null=True)
    tournament = models.ForeignKey(BhTournament, models.DO_NOTHING, blank=True, null=True)
    last_sync_at = models.PositiveIntegerField()
    season_cup_tournament_id = models.IntegerField(blank=True, null=True)
    season_tournament_category_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bh_tournament_event'


class BhTournamentFinalRanking(models.Model):
    rank = models.SmallIntegerField()
    points = models.SmallIntegerField()
    series = models.ForeignKey(BhSeries, models.DO_NOTHING, blank=True, null=True)
    tournament_event = models.ForeignKey(BhTournamentEvent, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bh_tournament_final_ranking'


class BhTournamentSettings(models.Model):
    created_at = models.PositiveIntegerField()
    amount_players_report = models.SmallIntegerField()
    amount_officials_report = models.SmallIntegerField()
    tournament = models.ForeignKey(BhTournament, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bh_tournament_settings'


class BhTournamentStage(models.Model):
    created_at = models.PositiveIntegerField()
    name = models.CharField(max_length=50)
    short_name = models.CharField(max_length=5)
    tournament_stage = models.CharField(max_length=20)
    order = models.SmallIntegerField()
    tournament_event = models.ForeignKey(BhTournamentEvent, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bh_tournament_stage'


class BhTournamentStates(models.Model):
    created_at = models.PositiveIntegerField()
    tournament_state = models.CharField(max_length=20)
    name = models.CharField(max_length=50)
    abbreviation = models.CharField(max_length=3, blank=True, null=True)
    max_number_teams = models.SmallIntegerField()
    min_number_teams = models.SmallIntegerField()
    hierarchy = models.SmallIntegerField()
    grid_row = models.SmallIntegerField()
    grid_col = models.SmallIntegerField()
    direct_compare = models.IntegerField()
    is_populated = models.IntegerField()
    is_final = models.IntegerField()
    is_finished = models.IntegerField()
    transitions_done = models.IntegerField()
    comment = models.CharField(max_length=50)
    color = models.CharField(max_length=7)
    tournament_event = models.ForeignKey(BhTournamentEvent, models.DO_NOTHING, blank=True, null=True)
    tournament_stage = models.ForeignKey(BhTournamentStage, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bh_tournament_states'


class BhTournamentTeamTransition(models.Model):
    created_at = models.PositiveIntegerField()
    origin_rank = models.SmallIntegerField()
    target_rank = models.SmallIntegerField()
    keep_stats = models.IntegerField()
    is_executed = models.IntegerField()
    comment = models.CharField(max_length=50)
    origin_ts_id = models.ForeignKey(BhTournamentStates, models.DO_NOTHING, blank=True, null=True)
    target_ts_id = models.ForeignKey(BhTournamentStates, models.DO_NOTHING, blank=True, null=True)
    tournament_event = models.ForeignKey(BhTournamentEvent, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bh_tournament_team_transition'


class BhTsRanking(models.Model):
    rank = models.SmallIntegerField()
    next_ts = models.ForeignKey(BhTournamentStates, models.DO_NOTHING, blank=True, null=True)
    ts = models.ForeignKey(BhTournamentStates, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bh_ts_ranking'


class BhTsSorting(models.Model):
    sorting = models.CharField(max_length=13)
    priority = models.SmallIntegerField()
    comment = models.CharField(max_length=50)
    tournament_state = models.ForeignKey(BhTournamentStates, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bh_ts_sorting'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'
