from django.conf import settings as conf_settings
import requests

from beachhandball_app.models.Tournaments import Tournament, TournamentEvent

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
        if not gbo_user.is_online:
            return gbo_user.subject_id
            
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
        if not gbo_user.is_online:
            return 'offline'
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
            if data:
                act_season = data[0]['season']['name']
        else:
            act_season = 'error'
        return data

    @staticmethod
    def syncTournamentData(gbo_user):
        # request data from sws
        endpoint = '/season/cup-tournaments/to/' + str(gbo_user.subject_id)
        headers = SWS.headers
        headers['Authorization'] = 'Bearer {}'.format(gbo_user.token)
        response = requests.get(SWS.base_url + endpoint, headers=headers)
        return response.json()

    @staticmethod
    def getTeamById(gbo_user, team_id):
        # request data from sws
        endpoint = '/season/team/' + str(team_id)
        headers = SWS.headers
        headers['Authorization'] = 'Bearer {}'.format(gbo_user.token)
        response = requests.get(SWS.base_url + endpoint, headers=headers)
        if response.json()['isError'] is not True:
            data = response.json()['message']
        else:
            data = None
        return data

    @staticmethod
    def getTeamTournamentById(gbo_user, team_tourn_id):
        # request data from sws
        endpoint = '/request/season-team-tournament/' + str(team_tourn_id)
        headers = SWS.headers
        headers['Authorization'] = 'Bearer {}'.format(gbo_user.token)
        response = requests.get(SWS.base_url + endpoint, headers=headers)
        if response.json()['isError'] is not True:
            data = response.json()['message']
        else:
            data = None
        return data

    @staticmethod
    def getTeamsOfTournamentById(gbo_user, tourn_id):
        # request data from sws
        endpoint = '/season/team-cup-tournament-ranking/' + str(tourn_id)
        headers = SWS.headers
        headers['Authorization'] = 'Bearer {}'.format(gbo_user.token)
        response = requests.get(SWS.base_url + endpoint, headers=headers)
        if response.json()['isError'] is not True:
            data = response.json()['message']
        else:
            data = None
        return data

    @staticmethod
    def getSeasonTeamCupTournamentRanking(gbo_user):
        # request data from sws
        endpoint = '/season/team-cup-tournament-ranking/'
        headers = SWS.headers
        headers['Authorization'] = 'Bearer {}'.format(gbo_user.token)
        response = requests.get(SWS.base_url + endpoint, headers=headers)
        return response.json()

    @staticmethod
    def getTeams(gbo_user):
        # request data from sws
        endpoint = '/season/team/'
        headers = SWS.headers
        headers['Authorization'] = 'Bearer {}'.format(gbo_user.token)
        response = requests.get(SWS.base_url + endpoint, headers=headers)
        return response.json()
    