# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models

from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django_unixdatetimefield import UnixDateTimeField
import jsonfield

class GBOUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gbo_user = models.CharField(max_length=100)
    gbo_data = jsonfield.JSONField()
    token = models.TextField(max_length=512)
    validUntil = UnixDateTimeField(null=False, default=0)
    subject_id = models.IntegerField(null=True)
    is_online = models.BooleanField(default=True)

    def __str__(self):
        return '{} {}, {} {}'.format(self.user.id, self.user.last_name, self.user.first_name, self.user.email)
