# tournament/views.py
from rest_framework import viewsets
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
from .services import generate_matches_for_phase
from django.shortcuts import render, get_object_or_404
import json

def cup_manager(request, event_id):
    return render(request, "cup_manager/cup_manager.html", {
        "event_id": event_id,
        "current_view": "basic_setup"})

def basic_setup(request, event_id):
    return render(request, "cup_manager/basic_setup.html", {
        "event_id": event_id,
        "current_view": "basic_setup"})

def structure_editor(request, event_id):
    return render(request, "cup_manager/structure_editor.html", {
        "event_id": event_id,
        "current_view": "structure"})

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

class CourtViewSet(viewsets.ModelViewSet):
    queryset = Court.objects.all()
    serializer_class = CourtSerializer

    def perform_create(self, serializer):
        event = serializer.validated_data['event']
        max_number = Court.objects.filter(event=event).aggregate(models.Max('court_number'))['court_number__max'] or 0
        serializer.save(court_number=max_number + 1)

class TimeSlotViewSet(viewsets.ModelViewSet):
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class StructureViewSet(viewsets.ModelViewSet):
    queryset = Structure.objects.all()
    serializer_class = StructureSerializer

class PhaseViewSet(viewsets.ModelViewSet):
    queryset = Phase.objects.all()
    serializer_class = PhaseSerializer

    # @action(detail=True, methods=["post"])
    # def generate_matches(self, request, pk=None):
    #     phase = self.get_object()

    #     # Call your match generation logic here
    #     generate_matches_for_phase(phase)

    #     return Response({"detail": "Matches generated."}, status=status.HTTP_200_OK)

class TransitionViewSet(viewsets.ModelViewSet):
    queryset = Transition.objects.all()
    serializer_class = TransitionSerializer

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

    def get_queryset(self):
        queryset = Team.objects.all()
        category_id = self.request.query_params.get('category', None)
    
        if category_id is not None:
            # Make sure we're filtering by exactly this category
            queryset = queryset.filter(category_id=category_id)
        
        return queryset

    # Add a custom action for team assignment
    @action(detail=True, methods=['POST'])
    def assign_to_slot(self, request, pk=None):
        try:
            # Get the team to be assigned
            team = self.get_object()
        
            # Get parameters from request data
            slot_id = request.data.get('slot_id')
            group_id = request.data.get('group_id')
        
            if not slot_id or not group_id:
                return Response({"detail": "Both slot_id and group_id are required"}, 
                                status=status.HTTP_400_BAD_REQUEST)
        
            # Get the slot team and group
            slot_team = Team.objects.get(pk=slot_id)
            group = Group.objects.get(pk=group_id)
        
            # Find the GroupTeam relationship for the slot
            try:
                group_team_rel = GroupTeam.objects.get(team=slot_team, group=group)
                position = group_team_rel.position
            
                # Delete the GroupTeam relationship for the slot
                group_team_rel.delete()
            
                # Create a new GroupTeam for the real team at the same position
                GroupTeam.objects.create(
                    team=team,
                    group=group,
                    position=position
                )
            
                # Delete the old slot team now that its relationship is gone
                slot_team.delete()
            
                return Response({"detail": "Team successfully assigned preserving position"}, 
                               status=status.HTTP_200_OK)
            
            except GroupTeam.DoesNotExist:
                return Response({"detail": "Slot is not properly associated with group"}, 
                               status=status.HTTP_400_BAD_REQUEST)
        
        except Team.DoesNotExist:
            return Response({"detail": "Team or slot not found"}, 
                           status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response({"detail": "Group not found"}, 
                           status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, 
                           status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST'])
    def unassign_from_group(self, request, pk=None):
        try:
            # Get the team to be unassigned
            team = self.get_object()
        
            # Get parameters from request data
            group_id = request.data.get('group_id')
        
            if not group_id:
                return Response({"detail": "Group ID is required"}, 
                                status=status.HTTP_400_BAD_REQUEST)
        
            # Get the group
            group = Group.objects.get(pk=group_id)
        
            # Find the GroupTeam relationship
            try:
                group_team_rel = GroupTeam.objects.get(team=team, group=group)
                position = group_team_rel.position
            
                # Create a new slot team
                category = team.category
                slot_team = Team.objects.create(
                    name=f"Slot - {group.name}",
                    category=category,
                    type='SLOT'
                )
            
                # Delete the GroupTeam for the real team
                group_team_rel.delete()
            
                # Create a new GroupTeam for the slot at the same position
                GroupTeam.objects.create(
                    team=slot_team,
                    group=group,
                    position=position
                )
            
                return Response({
                    "detail": "Team successfully unassigned and slot created at same position",
                    "slot_team_id": slot_team.id
                }, status=status.HTTP_200_OK)
            
            except GroupTeam.DoesNotExist:
                return Response({"detail": "Team isn't properly associated with this group"}, 
                               status=status.HTTP_400_BAD_REQUEST)
        
        except Team.DoesNotExist:
            return Response({"detail": "Team not found"}, 
                           status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response({"detail": "Group not found"}, 
                           status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, 
                           status=status.HTTP_400_BAD_REQUEST)

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            group = self.get_object()
            delete_slots = False
            preserve_real_teams = False
        
            # Parse the request body if it exists
            if request.body:
                try:
                    data = json.loads(request.body)
                    delete_slots = data.get('delete_slots', False)
                    preserve_real_teams = data.get('preserve_real_teams', False)
                except json.JSONDecodeError:
                    pass
            
            if delete_slots:
                # Get all teams in this group
                group_teams = Team.objects.filter(groups=group)
            
                # If we need to preserve real teams, only delete the SLOT type teams
                if preserve_real_teams:
                    slot_teams = group_teams.filter(type='SLOT')
                    slot_count = slot_teams.count()
                    slot_teams.delete()
                else:
                    # Otherwise delete all teams in the group
                    slot_count = group_teams.count()
                    group_teams.delete()
                
                # Delete the group itself
                response = super().destroy(request, *args, **kwargs)
            
                response.data = {"message": f"Group and {slot_count} slot teams deleted"}
                return response
            else:
                return super().destroy(request, *args, **kwargs)
            
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)



@csrf_exempt
def save_structure_template(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    try:
        data = json.loads(request.body)
        category_id = data['category_id']
        template_type = data['type']
        num_teams = data['num_teams']
        teams_per_group = data['teams_per_group']
        num_knockout = data.get('num_knockout_teams')
        num_placement = data.get('num_placement_teams')

        category = Category.objects.get(id=category_id)

        # Ensure structure exists
        structure, _ = Structure.objects.get_or_create(category=category)

        # Update or create template
        template, _ = StructureTemplate.objects.update_or_create(
            category=category,
            defaults={
                'type': template_type,
                'num_teams': num_teams,
                'teams_per_group': teams_per_group,
                'num_knockout_teams': num_knockout,
                'num_placement_teams': num_placement,
            }
        )

        return JsonResponse({'status': 'ok', 'template_id': template.id})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@api_view(["POST"])
def generate_matches_view(request, phase_id):
    try:
        phase = Phase.objects.get(pk=phase_id)
        num_teams = request.data.get("num_teams")
        teams_per_group = request.data.get("teams_per_group")

        if phase.name.upper() == "GROUP" and (not num_teams or not teams_per_group):
            return Response({"detail": "Number of groups and teams per group are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        generate_matches_for_phase(phase, num_teams=num_teams, teams_per_group=teams_per_group)
        return Response({"detail": "Matches generated successfully."})
    except Phase.DoesNotExist:
        return Response({"detail": "Phase not found."}, status=status.HTTP_404_NOT_FOUND)