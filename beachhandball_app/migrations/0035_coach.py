# Generated by Django 2.2.10 on 2021-06-04 22:34

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_unixdatetimefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('beachhandball_app', '0034_auto_20210605_0012'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coach',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', django_unixdatetimefield.fields.UnixDateTimeField(default=django.utils.timezone.now, editable=False)),
                ('name', models.CharField(max_length=50)),
                ('first_name', models.CharField(blank=True, max_length=50, null=True)),
                ('birthday', models.DateField(blank=True, null=True)),
                ('season_team_id', models.IntegerField(null=True)),
                ('season_coach_id', models.IntegerField(null=True)),
                ('gbo_position', models.CharField(blank=True, max_length=50, null=True)),
                ('team', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='beachhandball_app.Team')),
                ('tournament_event', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='beachhandball_app.TournamentEvent')),
            ],
            options={
                'db_table': 'bh_coach',
            },
        ),
    ]
