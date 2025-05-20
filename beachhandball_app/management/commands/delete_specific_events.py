from django.core.management.base import BaseCommand
from beachhandball_app.models.Tournaments import TournamentEvent

class Command(BaseCommand):
    help = "Deletes TournamentEvent objects with IDs 138 and 139 if they exist."

    def handle(self, *args, **options):
        ids_to_delete = [138, 139]
        events = TournamentEvent.objects.filter(id__in=ids_to_delete)
        count = events.count()
        if count == 0:
            self.stdout.write(self.style.WARNING("No TournamentEvent with IDs 138 or 139 found."))
        else:
            events.delete()
            self.stdout.write(self.style.SUCCESS(f"Deleted {count} TournamentEvent(s) with IDs 138 and/or 139."))
