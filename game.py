import curses
import random
import time
from typing import List, Tuple

import config
import common

from config import Defaults


class Game:

    food = "@"
    char = "\u25AA" #"\u25A0"
    heads = ("\u25B9", "\u25C3", "\u25B5", "\u25BF")
    
    blank = " "
    
    def __init__(self, screen, _window):
        self.screen = screen
        self.window_state = _window
        
        self.game_state = {"current_state": "GAME"}
        self.game_score = {"score": 0}

        self.max_y, self.max_x = self.screen.getmaxyx()

    def update_window(self, value: str) -> None:
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
    """ Either Active or Paused """

    food = "@"
    char = "\u25AA" #"\u25A0"
    headchars = ("\u25B9", "\u25C3", "\u25B5", "\u25BF")

    def __init__(self, screen, _state: dict, _window: dict, _status: dict):
        super().__init__(screen, _window)

        self.screen = screen

        self.state = _state
        self.status = _status

        
    def reset(self):
        self.settings = common.load_settings()

        self.is_paused = False

        self.direction = 0
        self.head_pos = [1,1]
        self.body = [self.head_pos] * self.settings["init_length"]
        self.deadcell = self.body[-1][:]

        self.snake_speed = self.settings["speed"] * self.settings["acceleration"]

        self.food_pos = [
            random.randrange(2, self.max_y - 1), 
            random.randrange(2, self.max_x - 1)
        ]


    def _new_food(self):
        """ Searches a freee space and then places a new apple there """
        
        while True:
            new_pos = [
                random.randrange(2, self.max_y - 1), 
                random.randrange(2, self.max_x - 1)
            ]

            if self.screen.inch(*new_pos) == config.Keys.SPACE.value:
                self.food_pos = new_pos
                break

    def draw_game(self):

        if self.deadcell not in self.body:
            self.screen.addch(
                self.deadcell[0],
                self.deadcell[1],
                " "
            )

        headchar = self.heads[self.direction]
        self.screen.addch(
            self.head_pos[0], 
            self.head_pos[1], 
            headchar, 
            curses.A_BOLD|curses.color_pair(3)
        )

        self.screen.addch(
            self.body[1][0], 
            self.body[1][1], 
            self.char, 
            curses.color_pair(4)
        )

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


        elif action == ord("p") or action == ord("P"):
            pass



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
        
        if self.direction == 0:
            self.head_pos[1] += 1

        elif self.direction == 1:
            self.head_pos[1] -= 1

        elif self.direction == 2:
            self.head_pos[0] -= 1

        elif self.direction == 3:
            self.head_pos[0] += 1

        self.deadcell = self.body[-1][:]
        for i in range(len(self.body) -1, 0, -1):
            self.body[i] = self.body[i -1]

        self.body[0] = self.head_pos[:]

    def check_collision(self):
        
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
            return 

        self.draw_game()

        self.screen.addstr(0, 1, f" Score: {self.status['score']} ")
        self.screen.move(self.max_y - 1, self.max_x - 1)
        self.screen.refresh()

        sleep_time = self.snake_speed / len(self.body)
        sleep_time = sleep_time / 2 if self.direction in [0,1] else sleep_time
        
        time.sleep(sleep_time)







class GameDeath(Game):
    def __init__(self, screen, _state: dict, _window: dict, _status: dict):
        super().__init__(screen, _window)

        self.screen = screen

        self.state = _state
        self.status = _status


    def handle_keys(self, action):
        # todo: change into switch case when python 3.10 is used
        
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
        elements: Tuple[str] = (
            f"You got {self.status['score']} points",
            "Press Enter to play again",
            "Press Q to quit",
            "Press M to go to main menu",
        )


        max_y, max_x = self.screen.getmaxyx()
        offset = len(elements) * (-1)
        
        for idx, line in enumerate(elements):
            self.screen.addstr(
                max_y // 2 + offset + idx,
                max_x // 2 - len(line) // 2,
                line,
                0
            )


    def run(self):
        self.screen.clear()

        self.screen.border()
        self.draw_end()

    
        action = self.screen.getch()
        self.handle_keys(action)

        self.screen.clear()



 



