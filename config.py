from enum import Enum
from typing import TypedDict

class GameSettings(TypedDict):
    init_length: int
    growth_size: int
    speed: int
    acceleration: int
    food_count: int

class LeaderboardItem(TypedDict):
    time: str
    score: int


# default settings
default_settings: GameSettings = {
    "init_length": 5,
    "growth_size": 1,
    "speed": 2,
    "acceleration": 1,
    "food_count": 1
}


# Enums for easier value setting
class Modes(Enum):
    MENU = 0
    GAME = 1

class Keys(Enum):
    RETURN = ord("\n")
    SPACE  = ord(" ")
    KEY_M  = ord("m")
    ENTER = ord("\n")

class Defaults(Enum):
    GAME = "GAME"
    MENU = "MAIN"
    SNAKE = "ACTIVE"

