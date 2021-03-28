from django.conf import settings as conf_settings
import requests


class SWS():
    """ Service for GBO database
    """
    def __init__(self):
        print('init')

    base_url = conf_settings.SWS_BASE_URL
    headers = {'content-type':'application/json'}

    @staticmethod
    def create_session(user, pw):
        endpoint = '/gbo/users/login'
        response = requests.post(SWS.base_url + endpoint,
        json={'email': user, 'password': pw},
        headers=SWS.headers)
        if response.json()['isError'] is not True:
            data = response.json()
            print("Session to gbo created")

        return response.json()

    @staticmethod
    def getCupTournaments(gbo_user):
        return 0