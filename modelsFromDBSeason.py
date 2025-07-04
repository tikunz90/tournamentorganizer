# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class CriteriaSubjectLevel(models.Model):
    points = models.IntegerField()
    created_at_ts = models.IntegerField(blank=True, null=True)
    ts = models.IntegerField(blank=True, null=True)
    subjectlevelid = models.ForeignKey('SubjectLevel', models.DO_NOTHING, db_column='subjectLevelId', blank=True, null=True)  # Field name made lowercase.
    authgroupid = models.ForeignKey('AuthGroup', models.DO_NOTHING, db_column='authGroupId', blank=True, null=True)  # Field name made lowercase.
    seasonid = models.ForeignKey('Season', models.DO_NOTHING, db_column='seasonId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'criteria_subject_level'


class CupCriteria(models.Model):
    created_at_ts = models.IntegerField(blank=True, null=True)
    ts = models.IntegerField(blank=True, null=True)
    seasoncriteriaid = models.ForeignKey('SeasonCriteria', models.DO_NOTHING, db_column='seasonCriteriaId', blank=True, null=True)  # Field name made lowercase.
    seasoncupid = models.ForeignKey('SeasonCup', models.DO_NOTHING, db_column='seasonCupId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'cup_criteria'


class CupSubject(models.Model):
    points = models.IntegerField()
    created_at_ts = models.IntegerField(blank=True, null=True)
    ts = models.IntegerField(blank=True, null=True)
    seasonid = models.ForeignKey('Season', models.DO_NOTHING, db_column='seasonId', blank=True, null=True)  # Field name made lowercase.
    authgroupid = models.ForeignKey('AuthGroup', models.DO_NOTHING, db_column='authGroupId', blank=True, null=True)  # Field name made lowercase.
    seasoncupid = models.ForeignKey('SeasonCup', models.DO_NOTHING, db_column='seasonCupId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'cup_subject'


class CupSubjectLevel(models.Model):
    created_at_ts = models.IntegerField(blank=True, null=True)
    ts = models.IntegerField(blank=True, null=True)
    seasonid = models.ForeignKey('Season', models.DO_NOTHING, db_column='seasonId', blank=True, null=True)  # Field name made lowercase.
    seasoncupid = models.ForeignKey('SeasonCup', models.DO_NOTHING, db_column='seasonCupId', blank=True, null=True)  # Field name made lowercase.
    criteriasubjectlevelid = models.ForeignKey(CriteriaSubjectLevel, models.DO_NOTHING, db_column='criteriaSubjectLevelId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'cup_subject_level'


class SeasonCategory(models.Model):
    created_at_ts = models.IntegerField(blank=True, null=True)
    ts = models.IntegerField(blank=True, null=True)
    seasonid = models.ForeignKey('Season', models.DO_NOTHING, db_column='seasonId', blank=True, null=True)  # Field name made lowercase.
    categoryid = models.ForeignKey('Category', models.DO_NOTHING, db_column='categoryId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'season_category'


class SeasonCriteria(models.Model):
    points = models.IntegerField()
    created_at_ts = models.IntegerField(blank=True, null=True)
    ts = models.IntegerField(blank=True, null=True)
    seasonid = models.ForeignKey('Season', models.DO_NOTHING, db_column='seasonId', blank=True, null=True)  # Field name made lowercase.
    criteriaid = models.ForeignKey('Criteria', models.DO_NOTHING, db_column='criteriaId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'season_criteria'


class SeasonCup(models.Model):
    points = models.IntegerField()
    created_at_ts = models.IntegerField(blank=True, null=True)
    ts = models.IntegerField(blank=True, null=True)
    cupid = models.ForeignKey('Cup', models.DO_NOTHING, db_column='cupId', blank=True, null=True)  # Field name made lowercase.
    seasonid = models.ForeignKey('Season', models.DO_NOTHING, db_column='seasonId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'season_cup'


class SeasonCupTournament(models.Model):
    created_at_ts = models.IntegerField(blank=True, null=True)
    ts = models.IntegerField(blank=True, null=True)
    seasonid = models.ForeignKey('Season', models.DO_NOTHING, db_column='seasonId', blank=True, null=True)  # Field name made lowercase.
    seasoncupid = models.ForeignKey(SeasonCup, models.DO_NOTHING, db_column='seasonCupId', blank=True, null=True)  # Field name made lowercase.
    seasontournamentid = models.ForeignKey('SeasonTournament', models.DO_NOTHING, db_column='seasonTournamentId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'season_cup_tournament'


class SeasonSubject(models.Model):
    ispublished = models.IntegerField(db_column='isPublished')  # Field name made lowercase.
    created_at_ts = models.IntegerField(blank=True, null=True)
    ts = models.IntegerField(blank=True, null=True)
    subjectid = models.ForeignKey('Subject', models.DO_NOTHING, db_column='subjectId', blank=True, null=True)  # Field name made lowercase.
    seasonid = models.ForeignKey('Season', models.DO_NOTHING, db_column='seasonId', blank=True, null=True)  # Field name made lowercase.
    authgroupid = models.ForeignKey('AuthGroup', models.DO_NOTHING, db_column='authGroupId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'season_subject'


class SeasonSubjectWeek(models.Model):
    start_at_ts = models.BigIntegerField()
    end_at_ts = models.BigIntegerField()
    created_at_ts = models.IntegerField(blank=True, null=True)
    ts = models.IntegerField(blank=True, null=True)
    seasonid = models.ForeignKey('Season', models.DO_NOTHING, db_column='seasonId', blank=True, null=True)  # Field name made lowercase.
    seasonsubjectid = models.ForeignKey(SeasonSubject, models.DO_NOTHING, db_column='seasonSubjectId', blank=True, null=True)  # Field name made lowercase.
    seasonweekid = models.ForeignKey('SeasonWeek', models.DO_NOTHING, db_column='seasonWeekId', blank=True, null=True)  # Field name made lowercase.
    authgroupid = models.ForeignKey('AuthGroup', models.DO_NOTHING, db_column='authGroupId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'season_subject_week'


class SeasonTask(models.Model):
    task = models.CharField(max_length=255)
    isdone = models.IntegerField(db_column='isDone')  # Field name made lowercase.
    created_at_ts = models.IntegerField(blank=True, null=True)
    ts = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'season_task'


class SeasonTournament(models.Model):
    created_at_ts = models.IntegerField(blank=True, null=True)
    ts = models.IntegerField(blank=True, null=True)
    tournamentid = models.ForeignKey('Tournament', models.DO_NOTHING, db_column='tournamentId', blank=True, null=True)  # Field name made lowercase.
    seasonid = models.ForeignKey('Season', models.DO_NOTHING, db_column='seasonId', blank=True, null=True)  # Field name made lowercase.
    seasonsubjectid = models.ForeignKey(SeasonSubject, models.DO_NOTHING, db_column='seasonSubjectId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'season_tournament'


class SeasonTournamentWeek(models.Model):
    start_at_ts = models.BigIntegerField()
    end_at_ts = models.BigIntegerField()
    created_at_ts = models.IntegerField(blank=True, null=True)
    ts = models.IntegerField(blank=True, null=True)
    seasonweekid = models.ForeignKey('SeasonWeek', models.DO_NOTHING, db_column='seasonWeekId', blank=True, null=True)  # Field name made lowercase.
    seasontournamentid = models.ForeignKey(SeasonTournament, models.DO_NOTHING, db_column='seasonTournamentId', blank=True, null=True)  # Field name made lowercase.
    seasonid = models.ForeignKey('Season', models.DO_NOTHING, db_column='seasonId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'season_tournament_week'


class SeasonWeek(models.Model):
    name = models.CharField(max_length=255)
    name_code = models.CharField(max_length=255)
    start_at_ts = models.BigIntegerField()
    end_at_ts = models.BigIntegerField()
    created_at_ts = models.IntegerField(blank=True, null=True)
    ts = models.IntegerField(blank=True, null=True)
    seasonid = models.ForeignKey('Season', models.DO_NOTHING, db_column='seasonId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'season_week'


class SubCategory(models.Model):
    created_at_ts = models.IntegerField(blank=True, null=True)
    ts = models.IntegerField(blank=True, null=True)
    subseasonid = models.ForeignKey('SubSeason', models.DO_NOTHING, db_column='subSeasonId', blank=True, null=True)  # Field name made lowercase.
    categoryid = models.ForeignKey('Category', models.DO_NOTHING, db_column='categoryId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'sub_category'


class SubCriteriaSubjectLevel(models.Model):
    points = models.IntegerField()
    created_at_ts = models.IntegerField(blank=True, null=True)
    ts = models.IntegerField(blank=True, null=True)
    subjectlevelid = models.ForeignKey('SubjectLevel', models.DO_NOTHING, db_column='subjectLevelId', blank=True, null=True)  # Field name made lowercase.
    authgroupid = models.ForeignKey('AuthGroup', models.DO_NOTHING, db_column='authGroupId', blank=True, null=True)  # Field name made lowercase.
    subseasonid = models.ForeignKey('SubSeason', models.DO_NOTHING, db_column='subSeasonId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'sub_criteria_subject_level'


class SubCriterion(models.Model):
    points = models.IntegerField()
    created_at_ts = models.IntegerField(blank=True, null=True)
    ts = models.IntegerField(blank=True, null=True)
    subseasonid = models.ForeignKey('SubSeason', models.DO_NOTHING, db_column='subSeasonId', blank=True, null=True)  # Field name made lowercase.
    criteriaid = models.ForeignKey('Criteria', models.DO_NOTHING, db_column='criteriaId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'sub_criterion'


class SubCup(models.Model):
    points = models.IntegerField()
    created_at_ts = models.IntegerField(blank=True, null=True)
    ts = models.IntegerField(blank=True, null=True)
    cupid = models.ForeignKey('Cup', models.DO_NOTHING, db_column='cupId', blank=True, null=True)  # Field name made lowercase.
    subseasonid = models.ForeignKey('SubSeason', models.DO_NOTHING, db_column='subSeasonId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'sub_cup'


class SubCupCriterion(models.Model):
    created_at_ts = models.IntegerField(blank=True, null=True)
    ts = models.IntegerField(blank=True, null=True)
    subseasoncriteriaid = models.ForeignKey(SubCriterion, models.DO_NOTHING, db_column='subSeasonCriteriaId', blank=True, null=True)  # Field name made lowercase.
    subseasoncupid = models.ForeignKey(SubCup, models.DO_NOTHING, db_column='subSeasonCupId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'sub_cup_criterion'


class SubCupSubject(models.Model):
    points = models.IntegerField()
    created_at_ts = models.IntegerField(blank=True, null=True)
    ts = models.IntegerField(blank=True, null=True)
    subseasonid = models.ForeignKey('SubSeason', models.DO_NOTHING, db_column='subSeasonId', blank=True, null=True)  # Field name made lowercase.
    authgroupid = models.ForeignKey('AuthGroup', models.DO_NOTHING, db_column='authGroupId', blank=True, null=True)  # Field name made lowercase.
    subseasoncupid = models.ForeignKey(SubCup, models.DO_NOTHING, db_column='subSeasonCupId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'sub_cup_subject'


class SubCupSubjectLevel(models.Model):
    created_at_ts = models.IntegerField(blank=True, null=True)
    ts = models.IntegerField(blank=True, null=True)
    subseasonid = models.ForeignKey('SubSeason', models.DO_NOTHING, db_column='subSeasonId', blank=True, null=True)  # Field name made lowercase.
    subseasoncupid = models.ForeignKey(SubCup, models.DO_NOTHING, db_column='subSeasonCupId', blank=True, null=True)  # Field name made lowercase.
    subcriteriasubjectlevelid = models.ForeignKey(SubCriteriaSubjectLevel, models.DO_NOTHING, db_column='subCriteriaSubjectLevelId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'sub_cup_subject_level'


class SubSeasonCupTournament(models.Model):
    created_at_ts = models.IntegerField(blank=True, null=True)
    ts = models.IntegerField(blank=True, null=True)
    subseasonid = models.ForeignKey('SubSeason', models.DO_NOTHING, db_column='subSeasonId', blank=True, null=True)  # Field name made lowercase.
    subseasoncupid = models.ForeignKey(SubCup, models.DO_NOTHING, db_column='subSeasonCupId', blank=True, null=True)  # Field name made lowercase.
    seasontournamentid = models.ForeignKey(SeasonTournament, models.DO_NOTHING, db_column='seasonTournamentId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'sub_season_cup_tournament'


class SubSeasonTournamentWeek(models.Model):
    start_at_ts = models.BigIntegerField()
    end_at_ts = models.BigIntegerField()
    created_at_ts = models.IntegerField(blank=True, null=True)
    ts = models.IntegerField(blank=True, null=True)
    seasonweekid = models.ForeignKey(SeasonWeek, models.DO_NOTHING, db_column='seasonWeekId', blank=True, null=True)  # Field name made lowercase.
    seasontournamentid = models.ForeignKey(SeasonTournament, models.DO_NOTHING, db_column='seasonTournamentId', blank=True, null=True)  # Field name made lowercase.
    subseasonid = models.ForeignKey('SubSeason', models.DO_NOTHING, db_column='subSeasonId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'sub_season_tournament_week'


class SubTournamentCriteriaSubject(models.Model):
    created_at_ts = models.IntegerField(blank=True, null=True)
    ts = models.IntegerField(blank=True, null=True)
    subtournamentcriteriasubjectweekid = models.ForeignKey('SubTournamentCriteriaSubjectWeek', models.DO_NOTHING, db_column='subTournamentCriteriaSubjectWeekId', blank=True, null=True)  # Field name made lowercase.
    seasonsubjectid = models.ForeignKey(SeasonSubject, models.DO_NOTHING, db_column='seasonSubjectId', blank=True, null=True)  # Field name made lowercase.
    subseasonid = models.ForeignKey('SubSeason', models.DO_NOTHING, db_column='subSeasonId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'sub_tournament_criteria_subject'


class SubTournamentCriteriaSubjectWeek(models.Model):
    created_at_ts = models.IntegerField(blank=True, null=True)
    ts = models.IntegerField(blank=True, null=True)
    seasontournamentid = models.ForeignKey(SeasonTournament, models.DO_NOTHING, db_column='seasonTournamentId', blank=True, null=True)  # Field name made lowercase.
    subcriteriasubjectlevelid = models.ForeignKey(SubCriteriaSubjectLevel, models.DO_NOTHING, db_column='subCriteriaSubjectLevelId', blank=True, null=True)  # Field name made lowercase.
    subseasontournamentweekid = models.ForeignKey(SubSeasonTournamentWeek, models.DO_NOTHING, db_column='subSeasonTournamentWeekId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'sub_tournament_criteria_subject_week'


class SubTournamentCriterion(models.Model):
    created_at_ts = models.IntegerField(blank=True, null=True)
    ts = models.IntegerField(blank=True, null=True)
    seasontournamentid = models.ForeignKey(SeasonTournament, models.DO_NOTHING, db_column='seasonTournamentId', blank=True, null=True)  # Field name made lowercase.
    subseasoncriteriaid = models.ForeignKey(SubCriterion, models.DO_NOTHING, db_column='subSeasonCriteriaId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'sub_tournament_criterion'


class SubWeek(models.Model):
    name = models.CharField(max_length=255)
    name_code = models.CharField(max_length=255)
    start_at_ts = models.BigIntegerField()
    end_at_ts = models.BigIntegerField()
    created_at_ts = models.IntegerField(blank=True, null=True)
    ts = models.IntegerField(blank=True, null=True)
    subseasonid = models.ForeignKey('SubSeason', models.DO_NOTHING, db_column='subSeasonId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'sub_week'


class TournamentCategory(models.Model):
    created_at_ts = models.IntegerField(blank=True, null=True)
    ts = models.IntegerField(blank=True, null=True)
    seasontournamentid = models.ForeignKey(SeasonTournament, models.DO_NOTHING, db_column='seasonTournamentId', blank=True, null=True)  # Field name made lowercase.
    categoryid = models.ForeignKey('Category', models.DO_NOTHING, db_column='categoryId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tournament_category'


class TournamentCriteria(models.Model):
    created_at_ts = models.IntegerField(blank=True, null=True)
    ts = models.IntegerField(blank=True, null=True)
    seasontournamentid = models.ForeignKey(SeasonTournament, models.DO_NOTHING, db_column='seasonTournamentId', blank=True, null=True)  # Field name made lowercase.
    seasoncriteriaid = models.ForeignKey(SeasonCriteria, models.DO_NOTHING, db_column='seasonCriteriaId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tournament_criteria'


class TournamentCriteriaSubject(models.Model):
    created_at_ts = models.IntegerField(blank=True, null=True)
    ts = models.IntegerField(blank=True, null=True)
    tournamentcriteriasubjectweekid = models.ForeignKey('TournamentCriteriaSubjectWeek', models.DO_NOTHING, db_column='tournamentCriteriaSubjectWeekId', blank=True, null=True)  # Field name made lowercase.
    seasonsubjectid = models.ForeignKey(SeasonSubject, models.DO_NOTHING, db_column='seasonSubjectId', blank=True, null=True)  # Field name made lowercase.
    seasonid = models.ForeignKey('Season', models.DO_NOTHING, db_column='seasonId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tournament_criteria_subject'


class TournamentCriteriaSubjectWeek(models.Model):
    created_at_ts = models.IntegerField(blank=True, null=True)
    ts = models.IntegerField(blank=True, null=True)
    seasontournamentid = models.ForeignKey(SeasonTournament, models.DO_NOTHING, db_column='seasonTournamentId', blank=True, null=True)  # Field name made lowercase.
    criteriasubjectlevelid = models.ForeignKey(CriteriaSubjectLevel, models.DO_NOTHING, db_column='criteriaSubjectLevelId', blank=True, null=True)  # Field name made lowercase.
    seasontournamentweekid = models.ForeignKey(SeasonTournamentWeek, models.DO_NOTHING, db_column='seasonTournamentWeekId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tournament_criteria_subject_week'
