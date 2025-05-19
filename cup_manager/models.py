from django.db import models

class Event(models.Model):
    name = models.CharField(max_length=255)
    date_start = models.DateField()
    date_end = models.DateField()

    def __str__(self):
        return self.name


class Court(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='courts')
    name = models.CharField(max_length=100)
    court_number = models.IntegerField(default=1)

    class Meta:
        unique_together = ('event', 'court_number')  # Ensures uniqueness per event

    def __str__(self):
        return f"{self.name} (#{self.court_number})"


class TimeSlot(models.Model):
    court = models.ForeignKey(Court, related_name="time_slots", on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    description = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.court.name} - {self.start_time.strftime('%H:%M')} to {self.end_time.strftime('%H:%M')}"


class Category(models.Model):
    GENDER_CHOICES = [
        ('M', 'Men'),
        ('W', 'Women'),
        ('U18', 'Under 18'),
        ('U16', 'Under 16'),
        ('U14', 'Under 14'),
        ('U12', 'Under 12'),
        ('U10', 'Under 10'),
    ]
    event = models.ForeignKey(Event, related_name='categories', on_delete=models.CASCADE)
    name = models.CharField(max_length=10, choices=GENDER_CHOICES)
    description = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.get_name_display()} ({self.event.name})"


class Structure(models.Model):
    category = models.OneToOneField(Category, related_name='structure', on_delete=models.CASCADE)

    def __str__(self):
        return f"Structure for {self.category}"

class StructureTemplate(models.Model):
    TEMPLATE_CHOICES = [
        ('GROUP_ONLY', 'Only Group Phase'),
        ('GROUP_KO', 'Group Phase + Knockout'),
        ('GROUP_KO_PLACEMENT', 'Group Phase + Knockout + Placement'),
    ]

    category = models.OneToOneField('Category', on_delete=models.CASCADE, related_name='template')
    type = models.CharField(max_length=30, choices=TEMPLATE_CHOICES)

    num_teams = models.PositiveIntegerField()
    teams_per_group = models.PositiveIntegerField()

    num_knockout_teams = models.PositiveIntegerField(blank=True, null=True)
    num_placement_teams = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.get_type_display()} - {self.category}"

class Phase(models.Model):
    PHASE_CHOICES = [
        ('GROUP', 'Group Phase'),
        ('KNOCKOUT', 'Knockout Phase'),
        ('PLACEMENT', 'Placement Phase'),
        ('FINALS', 'Finals'),
    ]
    category = models.ForeignKey(Category, related_name='phases',null=True, on_delete=models.CASCADE)
    #structure = models.ForeignKey(Structure, related_name='phases',blank=True, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=20, choices=PHASE_CHOICES)
    order = models.PositiveIntegerField(help_text="Order in which this phase occurs")
    number_of_teams = models.PositiveIntegerField(null=True, blank=True)
    number_of_groups = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.get_name_display()} (Order {self.order})"


class Match(models.Model):
    phase = models.ForeignKey("Phase", related_name="matches", on_delete=models.CASCADE)
    group = models.ForeignKey("Group", related_name="groups",null=True, blank=True, on_delete=models.CASCADE)
    court = models.ForeignKey("Court", null=True, blank=True, on_delete=models.SET_NULL)
    team1 = models.ForeignKey("Team", related_name="matches_as_team1", on_delete=models.CASCADE)
    team2 = models.ForeignKey("Team", related_name="matches_as_team2", on_delete=models.CASCADE)
    team1_score = models.IntegerField(null=True, blank=True)
    team2_score = models.IntegerField(null=True, blank=True)
    winner = models.ForeignKey("Team", null=True, blank=True, on_delete=models.SET_NULL, related_name="won_matches")
    start_time = models.DateTimeField(null=True, blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.team1} vs {self.team2} ({self.phase.name})"

    def set_winner(self):
        if self.team1_score is not None and self.team2_score is not None:
            if self.team1_score > self.team2_score:
                self.winner = self.team1
            elif self.team2_score > self.team1_score:
                self.winner = self.team2
            else:
                self.winner = None  # Optional: raise error if draws not allowed
        else:
            self.winner = None

class Transition(models.Model):
    from_phase = models.ForeignKey(Phase, related_name='transitions_from', on_delete=models.CASCADE)
    to_phase = models.ForeignKey(Phase, related_name='transitions_to', on_delete=models.CASCADE)
    condition = models.CharField(max_length=255, help_text="e.g. 'Top 2 teams advance'")

    def __str__(self):
        return f"{self.from_phase} → {self.to_phase} ({self.condition})"


class Team(models.Model):
    TEAM_TYPE_CHOICES = [
        ('SLOT', 'Dummy/Slot - Placeholder'),
        ('GBO', 'GBO - Registered Team'),
        ('FUN', 'Fun - Default Team'),
    ]

    category = models.ForeignKey(Category, related_name='teams', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    type = models.CharField(
        max_length=10, 
        choices=TEAM_TYPE_CHOICES,
        default='FUN',
        help_text="Type of team: Slot=placeholder, GBO=registered, Fun=default"
    )

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


class GroupTeam(models.Model):
    """Through model for Team-Group relationship with order field"""
    group = models.ForeignKey('Group', on_delete=models.CASCADE)
    team = models.ForeignKey('Team', on_delete=models.CASCADE)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['position']
        unique_together = ['group', 'position']


class Group(models.Model):
    phase = models.ForeignKey(Phase, related_name='groups', on_delete=models.CASCADE)
    name = models.CharField(max_length=10)
    # Don't modify the existing 'teams' field yet
    # Use just one teams field with the through model
    teams = models.ManyToManyField(
        Team,
        through='GroupTeam',
        related_name='groups',
    )

    def __str__(self):
        return f"Group {self.name} ({self.phase})"
