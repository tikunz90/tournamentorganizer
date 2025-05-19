# tournament/serializers.py
from rest_framework import serializers
from .models import Event, Court, TimeSlot, Category, Structure, Phase, Transition, Team, Group, GroupTeam

class CourtSerializer(serializers.ModelSerializer):
    class Meta:
        model = Court
        fields = ['id', 'event', 'name', 'court_number']

class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ['id', 'court', 'start_time', 'end_time', 'description']

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['id', 'name', 'category', 'type']


class GroupTeamSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)
    
    class Meta:
        model = GroupTeam
        fields = ['team', 'position']

class GroupSerializer(serializers.ModelSerializer):
    ordered_teams = GroupTeamSerializer(many=True, read_only=True, source='groupteam_set')
    teams = TeamSerializer(many=True, read_only=True)  # Get teams directly
    num_teams = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Group
        fields = ['id', 'name', 'phase', 'teams', 'ordered_teams', 'num_teams']

    def create(self, validated_data):
        num_teams = validated_data.pop('num_teams', 0)
        group = Group.objects.create(**validated_data)
    
        # Create empty team slots if num_teams is provided
        if num_teams > 0:
            category = group.phase.category
            for i in range(1, num_teams + 1):
                # Create placeholder teams
                team = Team.objects.create(
                    category=category,
                    name=f"Slot {i} - {group.name}",
                    type='SLOT'
                )
                # Create the through model instance with position
                GroupTeam.objects.create(
                    group=group,
                    team=team,
                    position=i
                )
    
        return group


class PhaseSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True, read_only=True)

    class Meta:
        model = Phase
        fields = ['id','category', 'name', 'order', 'groups']

class TransitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transition
        fields = '__all__'

class StructureSerializer(serializers.ModelSerializer):
    phases = PhaseSerializer(many=True, read_only=True)

    class Meta:
        model = Structure
        fields = ['id', 'category', 'phases']

class CategorySerializer(serializers.ModelSerializer):
    phases = PhaseSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'event','description', 'phases']

class EventSerializer(serializers.ModelSerializer):
    courts = CourtSerializer(many=True, read_only=True)
    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'name', 'date_start', 'date_end', 'courts', 'categories']
