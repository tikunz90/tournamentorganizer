from django.core.management.base import BaseCommand
from cup_manager.models import Category, Team
import random

class Command(BaseCommand):
    help = 'Generate dummy teams for existing categories'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--per-category',
            type=int,
            default=8,
            help='Number of teams to create per category (default: 8)',
        )
        parser.add_argument(
            '--event-id',
            type=int,
            help='Specific event ID to create teams for (optional)',
        )

    def handle(self, *args, **kwargs):
        per_category = kwargs['per_category']
        event_id = kwargs.get('event_id')
        
        self.stdout.write("Generating dummy teams...")
        
        # Get categories to create teams for
        categories = Category.objects.all()
        if event_id:
            categories = categories.filter(event_id=event_id)
            
        if not categories:
            self.stdout.write(self.style.ERROR("No categories found. Please create categories first."))
            return
        
        # Team name prefixes for more realistic team names
        name_prefixes = [
            "Strikers", "Phoenix", "Lions", "Tigers", "Eagles", "Hawks", 
            "Knights", "Warriors", "Wolves", "Bears", "Dragons", "Sharks",
            "Vipers", "Cobras", "Panthers", "Jaguars", "Bulldogs", "Titans",
            "Legends", "United", "Athletic", "Royals", "Galaxy", "Stars"
        ]
        
        # City names for team variety
        city_names = [
            "New York", "London", "Paris", "Berlin", "Madrid", "Rome", "Tokyo",
            "Sydney", "Moscow", "Beijing", "Rio", "Cairo", "Dubai", "Mumbai",
            "Toronto", "Chicago", "Houston", "Miami", "Atlanta", "Seattle",
            "Boston", "Denver", "Las Vegas", "Vienna", "Barcelona", "Amsterdam"
        ]
        
        teams_created = 0
        
        for category in categories:
            existing_count = Team.objects.filter(category=category).count()
            self.stdout.write(f"Category '{category}' already has {existing_count} teams")
            
            # Generate teams for this category
            for i in range(per_category):
                city = random.choice(city_names)
                prefix = random.choice(name_prefixes)
                
                # Format: "New York Tigers M" for men's category
                team_name = f"{city} {prefix} {category.name}"
                
                # Check if team already exists
                if Team.objects.filter(category=category, name=team_name).exists():
                    continue
                    
                team = Team.objects.create(
                    category=category,
                    name=team_name
                )
                
                teams_created += 1
                
            self.stdout.write(f"Created teams for category '{category}'")
            
        self.stdout.write(self.style.SUCCESS(f"Successfully created {teams_created} dummy teams"))
