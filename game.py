from typing import Tuple

import config
import common

class Game:

    food = "@"
    char = "\u25AA" #"\u25A0"
    heads = ("\u25B9", "\u25C3", "\u25B5", "\u25BF")
    
    blank = " "
    
    def __init__(self, screen, _window):
        self.screen = screen
        self.window_state = _window
        
        self.game_state = {"current_state": "DEATH"}
        self.game_score = {"score": 0}

        self.settings = common.load_settings()

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


    def run(self):
        head = [1, 1]
        
        body = [self.head[:]] * self.settings["init_length"]
        deadcell = body[-1][:]
        startbody = len(body)

        foodmade = False
        
        paused = 0

        direction = 0  
        gameover = 0
        
        # main gameloop
        while not gameover:



            action = self.screen.getch()
            
            if action == ord("p"):
                self.screen.addstr(
                    self.screen.max_y - 1, 1, "Paused. Press P to continue.")
                
                paused = 1


            pass

    def __call__(self):

        state_death = GameDeath(self.screen, self.game_state, self.window_state, self.game_score)

        while True:
            if self.game_state["current_state"] == "GAME":
                self.screen.nodelay(1)


            elif self.game_state["current_state"] == "DEATH":
                self.screen.nodelay(0)
                state_death.run()   
                self.screen.clear()


            elif self.game_state["current_state"] == "QUIT":
                self.update_window("QUIT")
                self.screen.clear()

                self._update_state("DEATH")
                return 

            elif self.game_state["current_state"] == "MENU":
                self.update_window("MENU")
                self.screen.clear()

                return 


class GameWindow(Game):
    """ Either Active or Paused """
    
    pass

class GameDeath(Game):
    def __init__(self, screen, _state: dict, _window: dict, _status: dict):
        super().__init__(screen, _window)

        self.screen = screen

        self.state = _state
        self.status = _status


    def handle_keys(self, action):
        # todo: change into switch case when python 3.10 is used
        
        if action == config.Keys.ENTER.value:
            pass

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

        self.screen.addstr(
            max_y // 2 + offset + 5,
            max_x // 2 - len(line) // 2,
            self.state["current_state"],
            0
        )
    

        self.screen.refresh()
        

    def run(self):
        self.screen.refresh()

        self.screen.border()
        self.draw_end()
    
        action = self.screen.getch()
        self.handle_keys(action)

        self.screen.clear()



 



