import curses
import json
import sys

import config as CONFIG
from menu import Menu


class Window:
    """ Game will be handled with different states. And will """

    def __init__(self, height: int = 12, width: int = 40) -> None:
        self.game_state = "settings"
        self.loaded = False


        self.height: int = height
        self.width: int = width

        self.window_state = {"active_window": "MENU"}


    def init_screen(self) -> None:
        
        self.screen = curses.initscr()
        self.max_y, self.max_x = self.screen.getmaxyx()

        check_width = self.max_x < self.width 
        check_height = self.max_y < self.height

        if check_height or check_width:
            print("Dimensions of screen are not valid")
            self.end_screen()


        curses.start_color()
        # Default: 1, Food: 2, Head: 3, Body: 4
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)  
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK) 
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)    
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)  


        self.screen.keypad(1)
        curses.noecho()

        # loaded = True

    def load_settings(self, path: str):
        with open(path, "r") as source:
            data = json.load(source)
        
        if not data:
            with open(path, "w") as source:
                json.dump(CONFIG.efault_settings)
            data = CONFIG.default_settings

        self.settings: CONFIG.GameSettings = data


    def end_screen(self):
        curses.endwin()


    def clear(self):
        self.screen.clear()


    def run(self, screen):

        del screen
        if not self.loaded:
            self.init_screen()

        menu_window = Menu(self.screen, self.window_state)
        
        while True:
            if self.window_state["active_window"] == "MENU":
                menu_window()

            elif self.window_state["active_window"] == "GAME":
                pass

            elif self.window_state["active_window"] == "QUIT":
                curses.endwin()
                return 
            

