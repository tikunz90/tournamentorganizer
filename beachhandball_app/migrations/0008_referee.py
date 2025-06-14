# Generated by Django 2.2.10 on 2021-05-25 21:35

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_unixdatetimefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('beachhandball_app', '0007_tournamentsettings'),
    ]

    operations = [
        migrations.CreateModel(
            name='Referee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', django_unixdatetimefield.fields.UnixDateTimeField(default=django.utils.timezone.now, editable=False)),
                ('name', models.CharField(max_length=50)),
                ('first_name', models.CharField(blank=True, max_length=50, null=True)),
                ('abbreviation', models.CharField(blank=True, max_length=12, null=True)),
                ('gbo_subject_id', models.SmallIntegerField(default=0)),
                ('partner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='beachhandball_app.Referee')),
                ('tournament', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='beachhandball_app.Tournament')),
            ],
            options={
                'db_table': 'bh_referee',
            },
        ),
    ]
