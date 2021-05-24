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
    def getGBOUserId(gbo_user):
        endpoint = '/gbo/subjects/email/{}'.format(gbo_user.gbo_user)
        headers = SWS.headers
        headers['Authorization'] = 'Bearer {}'.format(gbo_user.token)
        response = requests.get(SWS.base_url + endpoint, headers=headers)
        subject_id = -1
        if response.json()['isError'] is not True:
            data = response.json()['message']
            subject_id = data[0]['id']
        return subject_id

    @staticmethod
    def getCupTournaments(gbo_user):
        return 0
    
    @staticmethod
    def getSeasonActive(gbo_user):
        endpoint = '/gbo/seasons/active'
        headers = SWS.headers
        headers['Authorization'] = 'Bearer {}'.format(gbo_user.token)
        response = requests.get(SWS.base_url + endpoint, headers=headers)
        act_season = ''
        if response.json()['isError'] is not True:
            data = response.json()['message']
            act_season = data[0]['name']
        else:
            act_season = 'error'
        return act_season

    @staticmethod
    def getTournamentByUser(gbo_user):
        endpoint = '/season/cup-tournaments/to/' + str(gbo_user.subject_id)
        headers = SWS.headers
        headers['Authorization'] = 'Bearer {}'.format(gbo_user.token)
        response = requests.get(SWS.base_url + endpoint, headers=headers)
        act_season = ''
        if response.json()['isError'] is not True:
            data = response.json()['message']
            act_season = data[0]['season']['name']
        else:
            act_season = 'error'
        return data