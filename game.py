import curses
import random
import time
from typing import List, Tuple

import config
import common

from config import Defaults


class Game:
    def __init__(self, screen, _window: dict) -> None:
        """ Initialize basic variables
        
        param: screen (_CursesWindow): The screen instance of curses
        param: _window: Information on which winodw is active (e.g. GAME or MENU)
        """
        self.screen = screen
        self.window_state = _window
        
        self.game_state = {"current_state": "DEATH"}
        self.game_score = {"score": 0}

        self.max_y: int
        self.max_x: int
        self.max_y, self.max_x = self.screen.getmaxyx()


    def update_window(self, value: str) -> None:
        """ Update the subwindows of the game instance
        
        Possible values include:
            - "DEATH": Brings the user to the death screen
            - "GAME": Brings the user to the main game instance
        """
        self.window_state["active_window"] = value


    def _update_state(self, value: str) -> None:
        """ Function to change the state within the subclasses 
        
        Chnages the state of the currently active Game window.
        Possible values are 
            - GAME: the main snake game
            - PAUSE: paused version of the snak game
            - DEATH: Death sreen when snake game ends

        :param value: new value for the current state
        """
        self.state["current_state"] = value


    def _update_score(self, value: int) -> None:
        """ Function to update the score of the snake game 
        
        Allows to manage the score and then show it in 
        the final death window

        :param value: new score value
        """

        self.status["score"] = value


    def __call__(self):

        state_death = GameDeath(self.screen, self.game_state, self.window_state, self.game_score)
        state_game = GameWindow(self.screen, self.game_state, self.window_state, self.game_score)
        state_game.reset()

        while True:
            if self.game_state["current_state"] == "GAME":
                self.screen.nodelay(1)
                state_game.run()

            elif self.game_state["current_state"] == "DEATH":
                self.screen.nodelay(0)
                state_death.run()   
                state_game.reset()
                self.screen.clear()


            elif self.game_state["current_state"] == "QUIT":
                self.update_window("QUIT")
                self.screen.clear()

                return 

            elif self.game_state["current_state"] == "MENU":
                self.update_window("MENU")
                self.screen.clear()

                state_death._update_state(Defaults.GAME.value)
                return 



class GameWindow(Game):

    # variables to store the respective charachters
    food = "@"
    char = "\u25AA" #"\u25A0"
    headchars = ("\u25B9", "\u25C3", "\u25B5", "\u25BF")

    def __init__(self, screen, _state: dict, _window: dict, _status: dict) -> None:
        """ Initalize class variables
        
        :param screen (_CursesScreen): cureses screen instance
        :param _state: which game subwindow is active
        :param _window: which main window is active (currently: GAME)
        :param _status: information about score
        """
        super().__init__(screen, _window)

        self.screen = screen

        self.state = _state
        self.status = _status

        
    def reset(self):
        self.settings = common.load_settings()
        self._update_score(0)

        self.is_paused = False

        # initalize starting position and direction
        self._start_position()
        self.body = [self.head_pos] * self.settings["init_length"]
        self.deadcell = self.body[-1][:]

        self.snake_speed = self.settings["speed"] * self.settings["acceleration"]

        self.food_pos = [
            random.randrange(2, self.max_y - 1), 
            random.randrange(2, self.max_x - 1)
        ]


    def _start_position(self) -> None:
        """ Given the random start location of the snake orient the 
        snake in a way such that it does not collide directly into the wall.
        
        Looks up which borders are closest and orients the snake into the 
        opposite direction.
        """
        self.head_pos : List[int]
        self.head_pos = [
            random.randrange(1, self.max_y - 1), 
            random.randrange(1, self.max_x - 1)
        ]

        # select up: 2 if pos is closes to the bottom and vice versa 
        vertical_dist = self.max_y - self.head_pos[0] 
        vertical_dir = 3 if vertical_dist >= self.max_y // 2 else 2

        # select left: 1 if pos is closes to the right and vice versa 
        horizontal_dist = self.max_x - self.head_pos[1]
        horizontal_dir = 0 if horizontal_dist >= self.max_x // 2 else 1
        
        # choose either one 
        self.direction: int
        self.direction = random.choice([vertical_dir, horizontal_dir])


    def _new_food(self):
        """ Searches a freee space and then places a new apple there """
        
        while True:
            new_pos = [
                random.randrange(1, self.max_y - 1), 
                random.randrange(1, self.max_x - 1)
            ]

            if self.screen.inch(*new_pos) == config.Keys.SPACE.value:
                self.food_pos = new_pos
                break


    def draw_game(self) -> None:
        """ Draws the differenct components of the game"""
        
        # overwrites the old (dead) cells by replacing the chars by empty strings
        if self.deadcell not in self.body:
            self.screen.addch(
                self.deadcell[0],
                self.deadcell[1],
                " "
            )

        # Draws the head of the snake according to the direction it looks
        headchar = self.heads[self.direction]
        self.screen.addch(
            self.head_pos[0], 
            self.head_pos[1], 
            headchar, 
            curses.A_BOLD|curses.color_pair(3)
        )

        # Draws the body 
        self.screen.addch(
            self.body[1][0], 
            self.body[1][1], 
            self.char, 
            curses.color_pair(4)
        )

        # draws the food
        self.screen.addch(
            self.food_pos[0],
            self.food_pos[1],
            ord(self.food),
            curses.A_BOLD| curses.color_pair(2)
        )


    def handle_menu(self, action: int) -> bool:
        """ Checks if any of the menu keys is pressed
        
        If the quit button is clicked returns True such that the 
        game terminates directly. Else returns None → which will
        do the same as returning False. Since the result is 
        cathced in an if statement
        
        Possible menue keys are
            - (P): Pauses the snake game
            - (Q): Quits the snake game  

        :param action: ascii value of pressed key
        """
        
        if action == ord("q") or action == ord("Q"):
            self._update_state("QUIT")
            self.screen.refresh()

            return True


    def handle_move(self, action: int) -> None:
        """ Handles the direction of the snake given a arrow key
        
        Addtionally prevents the snake to go into the opposite direction.
        Which is not a valid move since this would terminate the snake.

        :param action: ascii value of pressed key
        """
        if action == curses.KEY_UP and self.direction != 3:
            self.direction = 2

        elif action == curses.KEY_DOWN and self.direction != 2:
            self.direction = 3
        
        elif action == curses.KEY_RIGHT and self.direction != 1:
            self.direction = 0
        
        elif action == curses.KEY_LEFT and self.direction != 0:
            self.direction = 1

        return 


    def move_head(self):
        """ Moves the head position and adjusts the body """
        
        # right: 0, left: 1, up: 2, down: 3 
        if self.direction == 0:
            self.head_pos[1] += 1

        elif self.direction == 1:
            self.head_pos[1] -= 1

        elif self.direction == 2:
            self.head_pos[0] -= 1

        elif self.direction == 3:
            self.head_pos[0] += 1

        # sets the last body element to deadcell and
        # shifts the body elements by one 
        self.deadcell = self.body[-1][:]
        for i in range(len(self.body) -1, 0, -1):
            self.body[i] = self.body[i -1]

        # sets the new body item to the head pos
        self.body[0] = self.head_pos[:]


    def check_collision(self):
        """ Chks if the new position of the snake head is valid
        
        Given the new head position gets the char the new position
        has and compares it to the wall and food chars. Additionally 
        the method retuns a bool if the snake hit a wall which allows
        to break the game instantly instead of waitin for a complete tick

        :returns boolean: If the snake collided with a wall
        """
        
        n_char = self.screen.inch(*self.head_pos)
        
        # n_char value for @ sign
        if n_char == 2097728:
            self._update_score(self.status['score'] +1)
            
            for _ in range(self.settings["growth_size"]):
                self.body.append(self.body[-1])

            self._new_food()
        
        elif n_char == config.Keys.SPACE.value:
            pass
        
        else:
            self._update_state("DEATH")
            return False

        return True


    def run(self):
        """ Main Loop of Snake Game instance"""
        
        # draw the border
        self.screen.border()

        # handle the key inputs
        action = self.screen.getch()
        self.handle_menu(action)

        # allows to skip the sleep timer
        if self.handle_move(action):
            return

        # move the snake head
        self.move_head()

        valid_move = self.check_collision()

        if not valid_move:
            # break the game without sleeping
            return 

        self.draw_game()

        # draw score
        self.screen.addstr(0, 1, f" Score: {self.status['score']} ")
        self.screen.move(self.max_y - 1, self.max_x - 1)
        self.screen.refresh()

        sleep_time = 1 / self.snake_speed  
        sleep_time = sleep_time / 2 if self.direction in [0,1] else sleep_time
        
        time.sleep(sleep_time)



class GameDeath(Game):
    def __init__(self, screen, _state: dict, _window: dict, _status: dict):
        """ Initalize class variables
        
        :param screen (_CursesScreen): cureses screen instance
        :param _state: which game subwindow is active
        :param _window: which main window is active (currently: GAME)
        :param _status: information about score
        """
        super().__init__(screen, _window)

        self.screen = screen

        self.state = _state
        self.status = _status


    def handle_menu_keys(self, action: int):
        """ Handles the menu keys
        todo: change into switch case when python 3.10 is used instead

        :param action: ascii value of pressed key
        """
        
        
        if action == config.Keys.ENTER.value:
            self._update_state("GAME")
            self.screen.refresh()

        elif action == ord('m') or action == ord("M"):
            self._update_state("MENU")
            self.screen.refresh()
        
        elif action == ord('q') or action == ord("Q"):
            self._update_state("QUIT")
            self.screen.refresh()


    def draw_end(self):
        """ Drawing the end screen """
        elements: Tuple[str] = (
            f"You got {self.status['score']} points",
            "Press Enter to play again",
            "Press Q to quit",
            "Press M to go to main menu",
        )

        max_y: int
        max_x: int

        max_y, max_x = self.screen.getmaxyx()
        offset = len(elements) * (-1)
        
        # draw the menu elements with an offset
        for idx, line in enumerate(elements):
            self.screen.addstr(
                max_y // 2 + offset + idx,
                max_x // 2 - len(line) // 2,
                line,
                0
            )


    def run(self):
        """ Main window of death screen"""

        self.screen.clear()

        self.screen.border()
        self.draw_end()

    
        action = self.screen.getch()
        self.handle_menu_keys(action)

        self.screen.clear()



 



