# Generated by Django 2.2.10 on 2021-06-11 06:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('beachhandball_app', '0039_auto_20210609_2112'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='tournament_state',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='beachhandball_app.TournamentState'),
        ),
    ]
