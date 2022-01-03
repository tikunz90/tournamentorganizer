from django.conf import settings as conf_settings
import requests
import time

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
            subject_id = 0
            for user in data:
                authgroup_id = user['authGroup']['id']
                if authgroup_id != 4:
                    continue
                subject_id = user['id']
        return subject_id

    @staticmethod
    def getCupTournaments(gbo_user):
        return 0
    
    @staticmethod
    def getSeasonActive():
        endpoint = '/gbo/seasons/active'
        headers = SWS.headers
        #headers['Authorization'] = 'Bearer {}'.format(gbo_user.token)
        response = requests.get(SWS.base_url + endpoint, headers=headers)
        act_season = ''
        if response.json()['isError'] is not True:
            act_season = response.json()['message'][0]
        else:
            act_season = {'isError': True}
        return act_season

    @staticmethod
    def getSeasons(gbo_user):
        if not gbo_user.is_online:
            return 'offline'
        endpoint = '/gbo/seasons/'
        headers = SWS.headers
        headers['Authorization'] = 'Bearer {}'.format(gbo_user.token)
        response = requests.get(SWS.base_url + endpoint, headers=headers)
        seasons = []
        if response.json()['isError'] is not True:
            seasons = response.json()['message']
        return seasons

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
    def getTournamentGermanChampionshipByUser(gbo_user):
        endpoint = '/season/cup-german-championship/to/' + str(gbo_user.subject_id)
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
    def getTournamentSubByUser(gbo_user):
        endpoint = '/season/cup-german-championship/to/' + str(gbo_user.subject_id)
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
    def syncAllTournamentData(gbo_user):
        # request data from sws
        begin = time.time()
        endpoint = '/season/cup-tournaments/'
        headers = SWS.headers
        headers['Authorization'] = 'Bearer {}'.format(gbo_user.token)
        response = requests.get(SWS.base_url + endpoint, headers=headers)
        result = response.json()
        end = time.time()
        execution_time = end - begin
        return result, execution_time

    @staticmethod
    def syncTournamentData(gbo_user):
        # request data from sws
        begin = time.time()
        endpoint = '/season/cup-tournaments/to/' + str(gbo_user.subject_id) + '/team-info?season=' + str(gbo_user.season_active['id'])
        headers = SWS.headers
        headers['Authorization'] = 'Bearer {}'.format(gbo_user.token)
        response = requests.get(SWS.base_url + endpoint, headers=headers)
        result = response.json()
        end = time.time()
        execution_time = end - begin
        return result, execution_time

    @staticmethod
    def syncTournamentGCData(gbo_user):
        # request data from sws
        begin = time.time()
        endpoint = '/season/cup-german-championship/to/' + str(gbo_user.subject_id) + '/team-info'
        headers = SWS.headers
        headers['Authorization'] = 'Bearer {}'.format(gbo_user.token)
        response = requests.get(SWS.base_url + endpoint, headers=headers)
        result = response.json()
        end = time.time()
        execution_time = end - begin
        return result, execution_time

    @staticmethod
    def syncTournamentSubData(gbo_user):
        # request data from sws
        begin = time.time()
        endpoint = '/season/cup-german-championship/to/' + str(gbo_user.subject_id) + '/team-info'
        headers = SWS.headers
        headers['Authorization'] = 'Bearer {}'.format(gbo_user.token)
        response = requests.get(SWS.base_url + endpoint, headers=headers)
        result = response.json()
        end = time.time()
        execution_time = end - begin
        return result, execution_time

    @staticmethod
    def getTeamById(gbo_user, team_id):
        # request data from sws
        token = ''
        if type(gbo_user) is dict:
            token =gbo_user['token']
        else:
            token = gbo_user.token
        endpoint = '/season/team/' + str(team_id)
        headers = SWS.headers
        headers['Authorization'] = 'Bearer {}'.format(token)
        response = requests.get(SWS.base_url + endpoint, headers=headers)
        if response.json()['isError'] is not True:
            data = response.json()['message']
        else:
            data = None
        return data

    @staticmethod
    def getTeamTournamentById(gbo_user, team_tourn_id):
        # request data from sws
        token = ''
        if type(gbo_user) is dict:
            token =gbo_user['token']
        else:
            token = gbo_user.token
        endpoint = '/request/season-team-tournament/' + str(team_tourn_id)
        headers = SWS.headers
        headers['Authorization'] = 'Bearer {}'.format(token)
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
        token = ''
        if type(gbo_user) is dict:
            token =gbo_user['token']
        else:
            token = gbo_user.token
        #endpoint = '/season/team-cup-tournament-ranking/'
        endpoint = '/season/cup-tournaments/to/'+ str(gbo_user['subject_id']) +'/team-info'
        headers = SWS.headers
        headers['Authorization'] = 'Bearer {}'.format(token)
        response = requests.get(SWS.base_url + endpoint, headers=headers)
        return response.json()

    @staticmethod
    def getSeasonTeamCupChampionshipRanking(gbo_user):
        # request data from sws
        token = ''
        if type(gbo_user) is dict:
            token =gbo_user['token']
        else:
            token = gbo_user.token
        endpoint = '/season/team-cup-championship-ranking/'
        headers = SWS.headers
        headers['Authorization'] = 'Bearer {}'.format(token)
        response = requests.get(SWS.base_url + endpoint, headers=headers)
        return response.json()
    
    @staticmethod
    def getSeasonTeamSubCupTournamentRanking(gbo_user):
        # request data from sws
        token = ''
        if type(gbo_user) is dict:
            token =gbo_user['token']
        else:
            token = gbo_user.token
        endpoint = '/season/team-cup-tournament-ranking/'
        headers = SWS.headers
        headers['Authorization'] = 'Bearer {}'.format(token)
        response = requests.get(SWS.base_url + endpoint, headers=headers)
        return response.json()

    @staticmethod
    def getTeams(gbo_user):
        # request data from sws
        token = ''
        if type(gbo_user) is dict:
            token =gbo_user['token']
        else:
            token = gbo_user.token
        endpoint = '/season/team/'
        headers = SWS.headers
        headers['Authorization'] = 'Bearer {}'.format(token)
        response = requests.get(SWS.base_url + endpoint, headers=headers)
        return response.json()
    