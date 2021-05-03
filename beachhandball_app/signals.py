from datetime import datetime

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models.Tournament import Tournament, TournamentState, TournamentTeamTransition, Court
from .models.Team import Team, TeamStats
from .models.Game import Game


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
        
        # Create dummy games
        tstat = TeamStats.objects.all().filter(tournamentstate=instance)
        court = Court.objects.filter(tournament=instance.tournament_event.tournament).first()
        if tstat.count() == 2:
            team_a, cr = Team.objects.get_or_create(tournament_event=instance.tournament_event,
                                                tournamentstate=instance,
                                                name=tstat.first().name_table,
                                                is_dummy=True,
                                                category=instance.tournament_event.category)
            team_b, cr = Team.objects.get_or_create(tournament_event=instance.tournament_event,
                                                tournamentstate=instance,
                                                name=tstat.last().name_table,
                                                is_dummy=True,
                                                category=instance.tournament_event.category)
            team_a.save()
            team_b.save()
            g, cr = Game.objects.get_or_create(tournament=instance.tournament_event,
                                                team_a=team_a,
                                                team_st_a=tstat.first(),
                                                team_b=team_b,
                                                team_st_b=tstat.last(),
                                                tournament_state=instance,
                                                court=court,
                                                gamestate='APPENDING',
                                                gamingstate='Ready')
            g.save()
        else:
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
                                                        team_a=team_a,
                                                        team_st_a=act_team_stat,
                                                        team_b=team_b,
                                                        team_st_b=team_stat_b,
                                                        tournament_state=instance,
                                                        court=court,
                                                        gamestate='APPENDING',
                                                        gamingstate='Ready')
                    g.save()
    print('Leave create_new_tournamentstate: ', datetime.now())