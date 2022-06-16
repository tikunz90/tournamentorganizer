from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from beachhandball_app.api.serializers.game_report.serializer import UploadSerializer
from beachhandball_app.models.Game import Game

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
        file_uploaded = request.FILES.get('file_uploaded')
        fs = FileSystemStorage()
        filename = fs.save(file_uploaded.name, file_uploaded)
        content_type = file_uploaded.content_type

        game = Game.objects.get(id=pk)
        if game is None:
            message = "Game not found! id=" + str(pk)
        else:
            message = 'File OK'
        return Response({'message': message})