from enum import Enum
from typing import Tuple, TypedDict

class GameSettings(TypedDict):
    init_length: int
    growth_size: int
    speed: int
    acceleration: int



diff_names = ("Easy", "Medium", "Hard")
diff_values = (0.1, 0.05, 0.01)
speeds: dict = {name: val for name, val in zip(diff_names, diff_values)}

default_settings: GameSettings = {
    "init_length": 5,
    "growth_size": 1,
    "speed": 2,
    "acceleration": 1
}


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

