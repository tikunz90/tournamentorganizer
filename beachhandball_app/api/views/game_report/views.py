import os
from django.db.models.query import Prefetch
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from beachhandball_app.api.serializers.game_report.serializer import UploadSerializer
from beachhandball_app.game_report import helper_game_report
from beachhandball_app.models.Game import Game
from beachhandball_app.models.Player import Player, PlayerStats

class FileUploadView(APIView):
    parser_classes = (FileUploadParser,)

    def put(self, request, format=None):
        file_obj = request.FILES['game_report_file']
        fs = FileSystemStorage()
        filename = fs.save(file_obj.name, file_obj)
        uploaded_file_url = fs.url(filename)
        # do some stuff with uploaded file
        return Response(status=204)


class UploadGameReportViewSet(ViewSet):
    serializer_class = UploadSerializer

    def list(self, request):
        return Response("GET API")

    def create(self, request, pk):
        games = Game.objects.select_related("tournament", "tournament_event__category", "team_st_a__team", "team_st_b__team").prefetch_related(
            Prefetch("team_a__player_set", queryset=Player.objects.all(), to_attr="players"),
            Prefetch("team_b__player_set", queryset=Player.objects.all(), to_attr="players"),
            Prefetch("playerstats_set", queryset=PlayerStats.objects.select_related("tournament_event__category", "player__team", "teamstat").all(), to_attr="pstats")
        ).filter(id=pk)
        if games.count() < 1:
            result['msg'] = "Game not found! id=" + str(pk)
            result['isError'] = True
            return Response(result)
        game = games.first()
        file_uploaded = request.FILES.get('file_uploaded')
        fs = FileSystemStorage(location='uploaded_reports/' + str(game.tournament.id) + '/' + str(game.tournament_event.id) + '/')
        filename = fs.save(file_uploaded.name, file_uploaded)
        content_type = file_uploaded.content_type
        file_url = fs.url(filename)
        result = {'isError': False}
        result = helper_game_report.pre_import_single_game_report(game, os.path.join(fs.location, filename))
        return Response(result)