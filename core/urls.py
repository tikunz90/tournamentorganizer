# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import debug_toolbar

from django.contrib import admin
from django.urls import path, include  # add this

urlpatterns = [
    path('admin/', admin.site.urls),          # Django admin route
    path("", include("authentication.urls")), # Auth routes - login / register
    path("", include("beachhandball_app.urls")),             # UI Kits Html files
    path('api/', include("beachhandball_app.api.urls")),
    path('__debug__/', include(debug_toolbar.urls)),
]
