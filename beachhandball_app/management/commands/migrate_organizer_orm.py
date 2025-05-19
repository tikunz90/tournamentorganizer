from django.core.management.base import BaseCommand
from authentication.models import GBOUser
from beachhandball_app.models.Tournaments import Tournament

class Command(BaseCommand):
    help = 'Migrate Tournament.organizer to Tournament.organizer_orm ForeignKey'

    def handle(self, *args, **options):
        updated_count = 0
        for gbouser in GBOUser.objects.all():
            tournaments = Tournament.objects.filter(organizer=gbouser.subject_id)
            for t in tournaments:
                t.organizer_orm = gbouser
                t.save(update_fields=['organizer_orm'])
                updated_count += 1
        self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated_count} tournaments.'))