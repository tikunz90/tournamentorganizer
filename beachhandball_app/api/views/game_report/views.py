from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from beachhandball_app.api.serializers.game_report.serializer import UploadSerializer

class FileUploadView(APIView):
    parser_classes = (FileUploadParser,)

    def put(self, request, format=None):
        file_obj = request.FILES['game_report_file']
        fs = FileSystemStorage()
        filename = fs.save(file_obj.name, file_obj)
        uploaded_file_url = fs.url(filename)
        # do some stuff with uploaded file
        return Response(status=204)


class UploadViewSet(ViewSet):
    serializer_class = UploadSerializer

    def list(self, request):
        return Response("GET API")

    def create(self, request):
        file_uploaded = request.FILES.get('file_uploaded')
        fs = FileSystemStorage()
        filename = fs.save(file_uploaded.name, file_uploaded)
        content_type = file_uploaded.content_type
        response = "POST API and you have uploaded a {} file {}".format(content_type, filename)
        return Response(response)