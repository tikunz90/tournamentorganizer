# Generated by Django 2.2.10 on 2021-06-01 19:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('beachhandball_app', '0023_auto_20210601_2016'),
    ]

    operations = [
        migrations.RenameField(
            model_name='team',
            old_name='request_season_team_tournaments_id',
            new_name='season_team_cup_tournament_ranking_id',
        ),
    ]
