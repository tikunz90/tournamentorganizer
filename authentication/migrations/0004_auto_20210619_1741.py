# Generated by Django 2.2.10 on 2021-06-19 15:41

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0003_gbouser_gbo_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='gbouser',
            name='gbo_gc_data',
            field=jsonfield.fields.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='gbouser',
            name='gbo_sub_data',
            field=jsonfield.fields.JSONField(default=dict),
        ),
    ]
