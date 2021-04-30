# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

class BeachHandballConfig(AppConfig):
    name = 'beachhandball_app'
    verbose_name = _('beachhandball_app')

    def ready(self):
        import beachhandball_app.signals
