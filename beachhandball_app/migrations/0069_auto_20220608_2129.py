# Generated by Django 2.2.10 on 2022-06-08 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beachhandball_app', '0068_auto_20220608_2054'),
    ]

    operations = [
        migrations.AddField(
            model_name='gamereporttemplate',
            name='cell_category_men',
            field=models.CharField(default='M3', max_length=6),
        ),
        migrations.AddField(
            model_name='gamereporttemplate',
            name='cell_category_women',
            field=models.CharField(default='P3', max_length=6),
        ),
        migrations.AddField(
            model_name='gamereporttemplate',
            name='cell_court_number',
            field=models.CharField(default='R8', max_length=6),
        ),
        migrations.AddField(
            model_name='gamereporttemplate',
            name='cell_date',
            field=models.CharField(default='C10', max_length=6),
        ),
        migrations.AddField(
            model_name='gamereporttemplate',
            name='cell_game_id',
            field=models.CharField(default='T4', max_length=6),
        ),
        migrations.AddField(
            model_name='gamereporttemplate',
            name='cell_group_stage',
            field=models.CharField(default='I4', max_length=6),
        ),
        migrations.AddField(
            model_name='gamereporttemplate',
            name='cell_knockout_stage',
            field=models.CharField(default='I5', max_length=6),
        ),
        migrations.AddField(
            model_name='gamereporttemplate',
            name='cell_ref_a_name',
            field=models.CharField(default='B48', max_length=6),
        ),
        migrations.AddField(
            model_name='gamereporttemplate',
            name='cell_ref_b_name',
            field=models.CharField(default='B49', max_length=6),
        ),
        migrations.AddField(
            model_name='gamereporttemplate',
            name='cell_team_a_name',
            field=models.CharField(default='B8', max_length=6),
        ),
        migrations.AddField(
            model_name='gamereporttemplate',
            name='cell_team_b_name',
            field=models.CharField(default='G8', max_length=50),
        ),
        migrations.AddField(
            model_name='gamereporttemplate',
            name='cell_time',
            field=models.CharField(default='F10', max_length=6),
        ),
        migrations.AddField(
            model_name='gamereporttemplate',
            name='max_num_coaches',
            field=models.SmallIntegerField(default=2),
        ),
        migrations.AddField(
            model_name='gamereporttemplate',
            name='max_num_player',
            field=models.SmallIntegerField(default=10),
        ),
        migrations.AddField(
            model_name='gamereporttemplate',
            name='team_a_coach_name_col',
            field=models.CharField(default='B', max_length=6),
        ),
        migrations.AddField(
            model_name='gamereporttemplate',
            name='team_a_player_name_col',
            field=models.CharField(default='B', max_length=6),
        ),
        migrations.AddField(
            model_name='gamereporttemplate',
            name='team_a_player_number_col',
            field=models.CharField(default='A', max_length=6),
        ),
        migrations.AddField(
            model_name='gamereporttemplate',
            name='team_a_start_row',
            field=models.SmallIntegerField(default=13),
        ),
        migrations.AddField(
            model_name='gamereporttemplate',
            name='team_a_start_row_coaches',
            field=models.SmallIntegerField(default=25),
        ),
        migrations.AddField(
            model_name='gamereporttemplate',
            name='team_b_coach_name_col',
            field=models.CharField(default='B', max_length=6),
        ),
        migrations.AddField(
            model_name='gamereporttemplate',
            name='team_b_player_name_col',
            field=models.CharField(default='B', max_length=6),
        ),
        migrations.AddField(
            model_name='gamereporttemplate',
            name='team_b_player_number_col',
            field=models.CharField(default='A', max_length=6),
        ),
        migrations.AddField(
            model_name='gamereporttemplate',
            name='team_b_start_row',
            field=models.SmallIntegerField(default=30),
        ),
        migrations.AddField(
            model_name='gamereporttemplate',
            name='team_b_start_row_coaches',
            field=models.SmallIntegerField(default=42),
        ),
    ]
