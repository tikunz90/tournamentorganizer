# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from authentication.models import GBOUser

# Define an inline admin descriptor for Employee model
# which acts a bit like a singleton
class GBOUserInline(admin.StackedInline):
    model = GBOUser
    can_delete = False
    verbose_name_plural = 'gbousers'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (GBOUserInline,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
#admin.site.register(GBOUser)
