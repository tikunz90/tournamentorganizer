# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
 
from .models.General import TournamentCategory
from .models.Tournament import Tournament, TournamentEvent, TournamentFinalRanking, TournamentTeamTransition, Court
from .models.Tournament import TournamentStage, TournamentState
from .models.Team import Team, TeamStats
from .models.Player import Player, PlayerStats
from .models.Game import Game, GameAction
from .models.Series import Series, Season

admin.site.register(Tournament)
admin.site.register(TournamentEvent)
admin.site.register(TournamentCategory)
admin.site.register(TournamentStage)
admin.site.register(TournamentTeamTransition)
admin.site.register(Team)
admin.site.register(TeamStats)
admin.site.register(Player)
admin.site.register(PlayerStats)
admin.site.register(TournamentState)
admin.site.register(Game)
admin.site.register(GameAction)
admin.site.register(TournamentFinalRanking)
admin.site.register(Series)
admin.site.register(Season)

@admin.register(Court)
class CourtAdmin(admin.ModelAdmin):
    list_display = ( "name", "number" , "tournament_name_short", "created_at")
    list_filter = ("tournament", "number", "name",)
    search_fields = ("name__startswith", )

    def tournament_name_short(self, obj):
        return obj.tournament.name_short
    tournament_name_short.short_description = "Tournament"