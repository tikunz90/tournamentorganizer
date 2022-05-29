
CATEGORY_CHOICES = (
        ('MEN', 'MEN'),
        ('WOMEN', 'WOMAN'),
        ('man', 'man'),
        ('woman', 'woman'),
        ('MIXED', 'MIXED'),
    )

TOURNAMENT_STATE_CHOICES = (
        ('GROUPA', 'GROUPA'),
        ('GROUPB', 'GROUPB'),
        ('GROUPC', 'GROUPC'),
        ('GROUPD', 'GROUPD'),
        ('GROUPE', 'GROUPE'),
        ('GROUPF', 'GROUPF'),
        ('INTERROUND_A', 'INTERROUND_A'),
        ('INTERROUND_B', 'INTERROUND_B'),
        ('LOOSER_ROUND', 'LOOSER_ROUND'),
        ('ROUND_OF_16', 'ROUND_OF_16'),
        ('QUARTERFINALS', 'QUARTERFINALS'),
        ('SEMIFINALS', 'SEMIFINALS'),
        ('FINAL', 'FINAL'),
        ('FINAL_RANKING', 'FINAL_RANKING'),
    )

COLOR_CHOICES = [
        ("#FFFFFF", "white"),
        ("#000000", "black"),
        ("#2A25BE", "Persian Blue"),
        ("#FF0005", "red"),
        ("#FFF200", "yellow")
    ]

COLOR_CHOICES_DICT =	{
  "white": "#FFFFFF",
  "black": "#000000",
  "persianblue": "#2A25BE",
  "red": "#FF0005",
  "yellow": "#FFF200",
}

TOURNAMENT_STAGE_TYPE_CHOICES = (
        ('GROUP_STAGE', 'GROUP_STAGE'),
        ('MAIN_ROUND', 'MAIN_ROUND'),
        ('KNOCKOUT_STAGE', 'KNOCKOUT_STAGE'),
        ('PLAYOFF_STAGE', 'PLAYOFF_STAGE'),
        ('FINAL', 'FINAL'),
    )

TEAM_TOURNAMENT_REG = (
    ('PENDING', 'PENDING',),
    ('ACCEPTED', 'ACCEPTED',),
    ('REJECTED', 'REJECTED',),
)

NATIONALITY_CHOICES = (
    ('DEU', 'Germany'),
    ('NLD', 'Netherlands'),
    ('ESP', 'Spain'),
    ('DNK', 'Denmark'),
    ('POL', 'Poland'),
    ('CHE', 'Switzerland'),
    ('USA', 'United States')
)

COURT_CHOICES = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
        (6, 6),
    )

GAMESTATE_CHOICES = (
    ('APPENDING', 'APPENDING',),
    ('RUNNING', 'RUNNING',),
    ('FINISHED', 'FINISHED',),
)

GAMESTATE_SCOUTING_CHOICES = (
    ('APPENDING', 'APPENDING',),
    ('RUNNING', 'RUNNING',),
    ('FINISHED', 'FINISHED',),
)
