# Generated by Django 2.2.10 on 2023-05-30 21:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('beachhandball_app', '0077_remove_court_scoreboard_user'),
        ('authentication', '0010_livescoreuser'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='livescoreuser',
            name='court',
        ),
        migrations.AddField(
            model_name='livescoreuser',
            name='tournament',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='beachhandball_app.Tournament'),
        ),
    ]
