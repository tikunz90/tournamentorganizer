from enum import auto
from strenum import StrEnum


class ROUND_TYPES(StrEnum):
    GROUP = auto()
    ROUND_64 = auto()
    ROUND_32 = auto()
    ROUND_16 = auto()
    ROUND_8 = auto()
    ROUND_4 = auto()
    ROUND_2 = auto()
    PLAYOFF = auto()
    RANKING = auto()


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
        ('GROUPG', 'GROUPG'),
        ('GROUPH', 'GROUPH'),
        ('GROUPI', 'GROUPI'),
        ('GROUPJ', 'GROUPJ'),
        ('GROUPK', 'GROUPK'),
        ('GROUPL', 'GROUPL'),
        ('GROUPM', 'GROUPM'),
        ('GROUPN', 'GROUPN'),
        ('GROUPO', 'GROUPO'),
        ('INTERROUND_A', 'INTERROUND_A'),
        ('INTERROUND_B', 'INTERROUND_B'),
        ('LOOSER_ROUND', 'LOOSER_ROUND'),
        ('ROUND_OF_16', 'ROUND_OF_16'),
        ('QUARTERFINALS', 'QUARTERFINALS'),
        ('SEMIFINALS', 'SEMIFINALS'),
        ('FINAL', 'FINAL'),
        ('FINAL_RANKING', 'FINAL_RANKING'),
    )

KNOCKOUT_NAMES = {
    2: 'F',
    4: 'SF',
    8: 'QF',
    16: 'R16',
    32: 'R32',
    64: 'R64',
    128: 'R128'
}

class URLs(StrEnum):
    GOOGLE = 'www.google.com'

COLOR_CHOICES = [
        ("#BABABA", "gray"),
        ("#000000", "black"),
        ("#2A25BE", "Persian Blue"),
        ("#FF0005", "red"),
        ("#FFF200", "yellow"),
        ("#FFFFFF", "white"),
        ("#EFC501", "gold"),
    ]

COLOR_CHOICES_DICT =	{
  "gray": "#BABABA",
  "black": "#000000",
  "persianblue": "#2A25BE",
  "red": "#FF0005",
  "yellow": "#FFF200",
  "white": "#FFFFFF",
  "gold": "#EFC501",
}

COLOR_CHOICES_GROUP_MEN = [
        ("#00008B", "dark blue"),
        ("#0000FF", "blue"),
        ("#0096FF", "bright blue"),
        ("#ADD8E6", "light blue"),
        ("#7DF9FF", "electric blue"),
        ("#00FFFF", "cyan"),
        ("#F0FFFF", "azure"), 
    ]

COLOR_CHOICES_GROUP_MEN_DICT =	{
  "dark blue": "#00008B",
  "blue": "#0000FF",
  "brightblue": "#0096FF",
  "lightblue": "#ADD8E6",
  "electricblue": "#7DF9FF",
  "cyan": "#00FFFF",
  "azure": "#F0FFFF",
}

COLOR_CHOICES_GROUP_WOMEN = [
        ("#8B0000", "dark red"),
        ("#FF0000", "red"),
        ("#EE4B2B", "bright red"),
        ("#E97451", "burnt sienna"),
        ("#FF4433", "red orange"),
        ("#E0115F", "ruby red"),
        ("#F88379", "coral pink"), 
    ]

COLOR_CHOICES_GROUP_WOMEN_DICT =	{
  "dark red": "#8B0000",
  "red": "#FF0000",
  "brightred": "#EE4B2B",
  "burntsienna": "#E97451",
  "redorange": "#FF4433",
  "rubyred": "#E0115F",
  "coralpink": "#F88379",
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
    ('SUI', 'Switzerland'),
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
