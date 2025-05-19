from .models import Match, Team, Group, Structure, Phase, StructureTemplate
from django.db import transaction

def setup_structure_from_template(category):
    template = category.template

    # Clean existing structure
    category.phases.all().delete()

    # Create base structure
    structure = Structure.objects.create(category=category)

    # Group Phase
    group_phase = Phase.objects.create(name="Group", order=0, structure=structure)
    generate_matches_for_phase(group_phase, num_groups=template.num_teams // template.teams_per_group, teams_per_group=template.teams_per_group)

    if template.type in ['GROUP_KO', 'GROUP_KO_PLACEMENT']:
        ko_phase = Phase.objects.create(name="Knockout", order=1, structure=structure)
        # Logic to move top teams from group to knockout

    if template.type == 'GROUP_KO_PLACEMENT':
        placement_phase = Phase.objects.create(name="Placement", order=2, structure=structure)
        # Logic to assign placement teams

def generate_matches_for_phase(phase, num_teams=None, teams_per_group=None):
    with transaction.atomic():
        # Clear existing matches/groups if needed
        Match.objects.filter(phase=phase).delete()
        Group.objects.filter(phase=phase).delete()

        Team.objects.filter(category=phase.structure.category).delete()

        teams = list(Team.objects.filter(category=phase.structure.category).order_by("id"))

        # Create teams if there are none
        if not teams:
            # If no teams exist, create them dynamically based on the phase category
            for i in range(num_teams):  # Create 10 teams, adjust as needed
                Team.objects.create(category=phase.structure.category, name=f"Team {i + 1}")
            teams = list(Team.objects.filter(category=phase.structure.category).order_by("id"))

        if phase.name.upper() == "GROUP":
            if not num_teams or not teams_per_group:
                raise ValueError("Group phase requires num_teams and teams_per_group.")

            # Calculate the ideal number of teams per group and distribute them evenly
            group_teams = []
            group_size = teams_per_group

            # Ensure that teams are evenly distributed
            num_full_groups = len(teams) // group_size
            remaining_teams = len(teams) % group_size

            # Create groups with the full number of teams
            for i in range(num_full_groups):
                group_teams.append(teams[i * group_size:(i + 1) * group_size])

            # Add the remaining teams to the last group
            if remaining_teams > 0:
                group_teams.append(teams[num_full_groups * group_size:])

            # Create groups and assign teams
            for i, team_list in enumerate(group_teams):
                group = Group.objects.create(name=f"Group {chr(65 + i)}", phase=phase)

                # Clear existing teams in the group before assigning new ones
                group.teams.clear()

                # Assign the new list of teams
                group.teams.set(team_list)

                # Round-robin matches in the group
                for j in range(len(team_list)):
                    for k in range(j + 1, len(team_list)):
                        Match.objects.create(
                            phase=phase,
                            group=group,
                            team1=team_list[j],
                            team2=team_list[k],
                            order=j * len(team_list) + k
                        )

        else:
            # For Knockout / Placement: just pair teams in order
            for i in range(0, len(teams), 2):
                if i + 1 < len(teams):
                    Match.objects.create(
                        phase=phase,
                        team1=teams[i],
                        team2=teams[i + 1],
                        order=i // 2
                    )
                else:
                    # Odd number of teams: team gets a bye
                    Match.objects.create(
                        phase=phase,
                        team1=teams[i],
                        team2=None,
                        order=i // 2
                    )

def generate_matches_for_phase_old(phase):
    """
    Generate matches for a given phase.
    Handles group stages (round-robin) and knockout stages.
    """
    if phase.name.lower().startswith("group"):
        generate_group_stage_matches(phase)
    elif phase.name.lower() in ("quarterfinal", "semifinal", "final", "knockout"):
        generate_knockout_matches(phase)
    elif phase.name.lower() == "placement":
        generate_placement_matches(phase)

def generate_group_stage_matches(phase):
    for group in phase.groups.all():
        teams = list(group.teams.all())
        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                Match.objects.get_or_create(
                    phase=phase,
                    group=group,
                    team1=teams[i],
                    team2=teams[j],
                )

def generate_knockout_matches(phase):
    teams = list(Team.objects.filter(phase=phase))  # You may filter via qualifiers
    matches = []
    while len(teams) >= 2:
        team1 = teams.pop(0)
        team2 = teams.pop(0)
        match = Match.objects.create(
            phase=phase,
            team1=team1,
            team2=team2
        )
        matches.append(match)
    return matches

def generate_placement_matches(phase):
    # Add placement match logic if needed
    pass
