# beachhandball_app/management/commands/update_games_realtime.py
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
            tournament = Tournament.objects.get(id=selected_id)
        except Tournament.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Tournament with ID {selected_id} does not exist."))
            return

        # Get all events for the tournament
        events = TournamentEvent.objects.filter(tournament=tournament)
        games = Game.objects.filter(tournament_event__in=events, last_real_time_data=None, gamestate='FINISHED')

        if not games.exists():
            self.stdout.write(self.style.WARNING("No games found for this tournament."))
            return

        self.stdout.write(f"Updating {games.count()} games for tournament '{tournament.name}'...")

        for game in games:
            game.last_real_time_data = helper.update_game_real_time_data(game)
            game.save(update_fields=["last_real_time_data"])
            self.stdout.write(f"Updated Game ID: {game.id}")

        self.stdout.write(self.style.SUCCESS("All games updated successfully."))