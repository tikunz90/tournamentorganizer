# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from rest_framework import serializers

from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django_unixdatetimefield import UnixDateTimeField
import jsonfield

from beachhandball_app.models.Tournaments import Court

class GBOUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gbo_user = models.CharField(max_length=100)
    gbo_data_all = jsonfield.JSONField()
    gbo_data = jsonfield.JSONField()
    gbo_gc_data = jsonfield.JSONField()
    gbo_sub_data = jsonfield.JSONField()
    token = models.TextField(max_length=1024)
    validUntil = UnixDateTimeField(null=False, default=0)
    subject_id = models.IntegerField(null=True)
    is_online = models.BooleanField(default=True)
    season_active = jsonfield.JSONField()

    def __str__(self):
        return '{} {}, {} {}'.format(self.user.id, self.user.last_name, self.user.first_name, self.user.email)


class GBOUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = GBOUser
        fields = "__all__"
        
class ScoreBoardUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    court = models.OneToOneField(Court, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {}, {} {}'.format(self.user.id, self.user.last_name, self.user.first_name, self.user.email)

class ScoreBoardUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoreBoardUser
        fields = "__all__"
