# Generated by Django 2.2.10 on 2021-06-02 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beachhandball_app', '0027_tournament_gbo_tournament_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tournament',
            name='gbo_tournament_id',
            field=models.IntegerField(default=0),
        ),
    ]
