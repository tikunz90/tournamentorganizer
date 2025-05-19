from django.core.management.base import BaseCommand
from cup_manager.models import *
from datetime import date
import random

class Command(BaseCommand):
    help = 'Generate a dummy tournament with structure and teams'

    def handle(self, *args, **kwargs):
        self.stdout.write("Creating dummy tournament...")

        # Clear existing data
        Event.objects.all().delete()

        # Create event
        event = Event.objects.create(name="Spring Championship", date_start=date.today(), date_end=date.today())
        self.stdout.write(f"Event: {event}")

        # Add courts
        courts = [Court.objects.create(event=event, name=f"Court {i+1}", court_number=i+1) for i in range(3)]
        self.stdout.write(f"Created {len(courts)} courts")

        # Categories
        category_names = ['M', 'W', 'U18', 'U16']
        for name in category_names:
            cat = Category.objects.create(event=event, name=name)
            self.stdout.write(f"Category: {cat}")

            # Create teams
            #teams = [Team.objects.create(category=cat, name=f"Team {name}{i+1}") for i in range(6)]
            #self.stdout.write(f"Created {len(teams)} teams for {name}")

            # Create structure
            #structure = Structure.objects.create(category=cat)

            # Phases
            #group_phase = Phase.objects.create(structure=structure, name='GROUP', order=1)
            #knockout_phase = Phase.objects.create(structure=structure, name='KNOCKOUT', order=2)
            #finals_phase = Phase.objects.create(structure=structure, name='FINALS', order=3)

            # Transitions
            #Transition.objects.create(from_phase=group_phase, to_phase=knockout_phase, condition="Top 2 teams")
            #Transition.objects.create(from_phase=knockout_phase, to_phase=finals_phase, condition="Winners advance")

            # Group
            #group = Group.objects.create(phase=group_phase, name="A")
            #group.teams.set(teams)

            self.stdout.write(f"Structure with phases and group created for {name}")

        self.stdout.write(self.style.SUCCESS("Dummy tournament created successfully."))