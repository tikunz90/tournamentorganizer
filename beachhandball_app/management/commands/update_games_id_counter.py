from django.core.management.base import BaseCommand
from beachhandball_app.models.Tournaments import Tournament, TournamentEvent
from beachhandball_app.models.Game import Game
from beachhandball_app import helper

class Command(BaseCommand):
    help = "Update last_real_time_data for all games of a selected tournament"

    def handle(self, *args, **options):
        # List all tournaments
        tournaments = Tournament.objects.all()
        if not tournaments.exists():
            self.stdout.write(self.style.ERROR("No tournaments found."))
            return

        self.stdout.write("Available Tournaments:")
        for t in tournaments:
            self.stdout.write(f"  ID: {t.id} | Name: {t.name}")

        # Prompt for tournament ID
        try:
            selected_id = int(input("Enter the ID of the tournament to update: ").strip())
        except ValueError:
            self.stdout.write(self.style.ERROR("Invalid input. Please enter a valid integer ID."))
            return

        try:
            tournament = Tournament.objects.filter(id=selected_id).first()
        except Tournament.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Tournament with ID {selected_id} does not exist."))
            return

        updated_count = Game.renumber_game_counters(tournament.id)
        print(f"Updated {updated_count} games with new counter values")