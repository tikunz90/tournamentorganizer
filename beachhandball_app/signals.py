from datetime import datetime

from django.db.models import signals
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models.Tournament import Tournament, TournamentEvent, TournamentState, TournamentTeamTransition, Court
from .models.Team import Team, TeamStats
from .models.Game import Game
from .models.Player import Player, PlayerStats

from .models.choices import TOURNAMENT_STATE_CHOICES

from .helper import calculate_tstate

@receiver(post_save, sender=TournamentEvent)
def create_new_tournament_event(sender, instance, created, **kwargs):
    if created:
        # create final ranking
        ts = TournamentState.objects.create(tournament_event=instance,
                                            tournament_state=TOURNAMENT_STATE_CHOICES[-1][1],
                                            name='Final Ranking',
                                            abbreviation='FR',
                                            hierarchy=999,
                                            direct_compare=False,
                                            max_number_teams=instance.max_number_teams,
                                            is_final=True,
                                            comment='')

@receiver(post_save, sender=TournamentState)
def create_new_tournamentstate(sender, instance, created, **kwargs):
    print('Enter create_new_tournamentstate: ', datetime.now())
    if created:
        # Create dummy teamstats
        for i in range(1, instance.max_number_teams+1):
            new_dummy_team, cr = Team.objects.get_or_create(tournament_event=instance.tournament_event,
                                                            tournamentstate=instance,
                                                            name="{}. {}".format(i, instance),
                                                            abbreviation="{}.{}".format(i, instance.abbreviation),
                                                            category=instance.tournament_event.category,
                                                            is_dummy=True)

            act_team_st, cr = TeamStats.objects.get_or_create(tournament_event=instance.tournament_event,
                                                              tournamentstate=instance,
                                                              team=new_dummy_team,
                                                              rank_initial=i)

            if not instance.is_final:
                # create team transitions
                ttt = TournamentTeamTransition.objects.create(tournament_event=instance.tournament_event,
                                                              origin_rank=i,
                                                              origin_ts_id=instance,
                                                              target_rank=i,
                                                              keep_stats=False,
                                                              comment='')
            else:
                print('Do Final Table')
        if not instance.is_final:
            # Create dummy games
            tstat = TeamStats.objects.all().filter(tournamentstate=instance)
            court = Court.objects.filter(tournament=instance.tournament_event.tournament).first()
            teams = []
            for ts_tmp in tstat:
                teams.append(ts_tmp)

            while len(teams) > 1:
                act_team_stat = teams.pop(0)
                if act_team_stat.team is None:
                    team_a, cr = Team.objects.get_or_create(tournament_event=instance.tournament_event,
                                                            tournamentstate=instance,
                                                            name=act_team_stat.name_table,
                                                            is_dummy=True,
                                                            category=instance.tournament_event.category)
                else:
                    team_a = act_team_stat.team
                team_a.save()
                for team_stat_b in teams:
                    if team_stat_b.team is None:
                        team_b, cr = Team.objects.get_or_create(tournament_event=instance.tournament_event,
                                                                tournamentstate=instance,
                                                                name=team_stat_b.name_table,
                                                                is_dummy=True,
                                                                category=instance.tournament_event.category)
                        team_b.save()
                    else:
                        team_b = team_stat_b.team

                    g, cr = Game.objects.get_or_create(tournament=instance.tournament_event,
                                                        #team_a=team_a,
                                                        team_st_a=act_team_stat,
                                                        #team_b=team_b,
                                                        team_st_b=team_stat_b,
                                                        tournament_state=instance,
                                                        court=court,
                                                        gamestate='APPENDING',
                                                        gamingstate='Ready')
                    g.save()
    print('Leave create_new_tournamentstate: ', datetime.now())


@receiver(post_save, sender=TournamentTeamTransition)
def ttt_changed(sender, created, **kwargs):
    if not created and 'instance' in kwargs:
        # on update, set display name for team stat
        ttt = kwargs['instance']

        team_stats_tar = TeamStats.objects.all().filter(tournament_event=ttt.tournament_event,
                                                        tournamentstate=ttt.target_ts_id,
                                                        rank_initial=ttt.target_rank)
        if team_stats_tar.count() > 0:
            ts_tar = team_stats_tar.get()
            ts_tar.name_table = '{}. {}'.format(ttt.origin_rank, ttt.origin_ts_id)
            ts_tar.team.name = '{}. {}'.format(ttt.origin_rank, ttt.origin_ts_id)
            ts_tar.team.abbreviation = '{}. {}'.format(ttt.origin_rank, ttt.origin_ts_id.abbreviation)
            ts_tar.team.save()
            ts_tar.save()


@receiver(post_save, sender=Game)
def game_updated(sender, instance, created, **kwargs):
    if not created: 
        receivers = post_save.receivers
        post_save.receivers = []
        calculate_tstate(instance.tournament_state)
        post_save.receivers = receivers

@receiver(post_save, sender=Player)
def create_player_ranking_stat(sender, instance, created, **kwargs):
    if created:
        ps, cr = PlayerStats.objects.get_or_create(tournament_event=instance.tournament_event,
         player=instance, is_ranked=True)

        # set all to zero
        ps.games_played = 0
        ps.score = 0
        ps.kempa_try = 0
        ps.kempa_success = 0
        ps.spin_try = 0
        ps.spin_success = 0
        ps.shooter_try = 0
        ps.shooter_success = 0
        ps.one_try = 0
        ps.one_success = 0
        ps.suspension = 0
        ps.redcard = 0
        ps.save()
