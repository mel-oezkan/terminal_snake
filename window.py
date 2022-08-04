import curses

from game import Game
from menu import Menu


class Window:
    def __init__(self) -> None:
        """ Initalize class variables"""
        self.game_state = "settings"
        self.loaded = False

        self.window_state = {"active_window": "MENU"}


    def init_screen(self) -> None:
        """ Initalize curses screen and other variables"""

        self.screen = curses.initscr()

        curses.start_color()
        
        # set colors: Default: 1, Food: 2, Head: 3, Body: 4
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)  
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK) 
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)    
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)  

        self.screen.keypad(1)
        curses.noecho()


    def run(self, screen):
        """ Main Loop of the Game Window """
        
        del screen
        if not self.loaded:
            self.init_screen()

        # create the Game instances
        menu_window = Menu(self.screen, self.window_state)
        game_window = Game(self.screen, self.window_state)
        
        
        while True:
            
            # Handles the active Windows
            if self.window_state["active_window"] == "MENU":
                menu_window()
                self.screen.clear()
                continue 

            elif self.window_state["active_window"] == "GAME":
                game_window()
                self.screen.clear()
                continue 

            elif self.window_state["active_window"] == "QUIT":
                curses.endwin()
                self.screen.clear()
                return 
