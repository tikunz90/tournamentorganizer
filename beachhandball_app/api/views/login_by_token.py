from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
class LoginByToken(APIView):
    """
    View to list all users in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    authentication_classes = [authentication.TokenAuthentication]
    #permission_classes = [permissions.IsAdminUser]

    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        if 'RestSharp' in request.headers['User-Agent']:
            key = request.headers['AuthorizationToken'].strip().split()[1]
        else:
            key = request.META['HTTP_AUTHORIZATION'].strip().split()[1]
        print(key)
        data= {'IsKeyValid': 'false' }
        if key:
            data['IsKeyValid'] = 'true'
            user = Token.objects.get(key=key).user
            print(user)
            data['user'] = str(user)
        print('OK')
        return Response(data)