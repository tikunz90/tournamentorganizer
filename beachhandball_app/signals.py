from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models.Tournament import Tournament, TournamentState
from .models.Team import Team, TeamStats


@receiver(post_save, sender=TournamentState)
def create_new_tournamentstate(sender, instance, created, **kwargs):
    if created:
        # Create dummy teamstats
        for i in range(1, instance.max_number_teams+1):
            new_dummy_team, cr = Team.objects.get_or_create(tournament_event=instance.tournament_event,
                                                            name="{}. {}".format(i, instance),
                                                            category=instance.tournament_event.category,
                                                            is_dummy=True)

            act_team_st, cr = TeamStats.objects.get_or_create(tournament_event=instance.tournament_event,
                                                              tournamentstate=instance,
                                                              team=new_dummy_team,
                                                              rank_initial=i)

            if not instance.is_final:
                # create team transitions
                print("")
                #ttt = TournamentTeamTransition.objects.create(tournament=instance.tournament,
                #                                              origin_rank=i,
                #                                              origin_ts_id=instance,
                #                                              target_rank=i,
                #                                              keep_stats=False,
                #                                              comment='')
            else:
                print('Do Final Table')