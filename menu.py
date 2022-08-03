import json
import curses
import pathlib

from typing import Tuple

import common

from config import Defaults
from config import GameSettings
from config import Modes 
from config import Keys 
from config import default_settings

class Menu:
    def __init__(self, screen, _state) -> None:
        self.screen = screen
        self.screen.nodelay(Modes.MENU.value)

        
        self.menu_state = {"active_menu": "MAIN"}
        
        self.window_state = _state
        

    def update_window(self, value):
        self.window_state["active_window"] = value


    def draw_menu(self, menu_options: Tuple[str], graphics: Tuple[int]):
        """ Generic function that plots the given menu opitons
        according to the given graphics. (Graphics handles how
        the items are drawn)

        :param menu_options: Items to be displayed
        :param 
        """
        
        assert len(menu_options) == len(graphics), f"Menu args have to match in size \n {len(menu_options)} : {len(graphics)}"

        
        max_y, max_x = self.screen.getmaxyx()
        offset = len(menu_options) // 2 * (-1)

        for opt_str, attr in zip(menu_options, graphics):
            self.screen.addstr( 
                max_y //2 + offset,
                max_x //2 - len(opt_str)//2,
                opt_str,
                attr # color attribute
            )

            offset += 1
        
        self.screen.refresh()

    def handle_menu_actions(self, active_opt, action, graphics):
        """
        """
        
        if action == curses.KEY_UP:
            return (active_opt - 1) % len(graphics)
        
        elif action == curses.KEY_DOWN:
            return (active_opt + 1) % len(graphics)
        
        return active_opt


    def update_state(self, value):
        self.state["active_menu"] = value

    
    def __call__(self) -> None:
        
        main_menu = MainMenu(self.screen, self.menu_state, self.window_state)
        settings_menu = SettingsMenu(self.screen, self.menu_state, self.window_state)

        while True:
            if self.menu_state["active_menu"] == "MAIN":
                # self.graphics[self.active_option] = curses.A_REVERSE
                main_menu()
                
            elif self.menu_state["active_menu"] == "SETTINGS":
                settings_menu()

            elif self.menu_state["active_menu"] == "GAME":
                self.update_window("GAME")
                self.screen.clear()

                # set the menu state to main such that when coming
                # back the default value ("MAIN") will be set
                main_menu.update_state(Defaults.MENU.value)

                return 

            elif self.menu_state["active_menu"] == "QUIT":
                self.update_window("QUIT")
                self.screen.clear()

                return 

            else:
                raise ValueError



class MainMenu(Menu):
    options = ("Play", "Settings", "Help", "Exit")
    
    def __init__(self, screen, _state: dict, _window: dict):
        super().__init__(screen, _window)

        self.state = _state 
        self.active_option = 0

        self.graphics = [0, 0, 0, 0]
        self.graphics[self.active_option] = curses.A_REVERSE

    def handle_submit(self, active_option, action):
        if action == Keys.ENTER.value:

            if active_option == 0:
                self.update_state("GAME")
                self.screen.refresh()

            elif active_option == 1:
                self.update_state("SETTINGS")
                self.screen.clear()

            elif active_option == 2:
                self.update_state("HELP")
                self.screen.clear()

            elif active_option == 3:
                self.update_state("QUIT")
                self.screen.clear()


    def __call__(self) -> None:
        # Main loop for the main Menu        
        self.screen.clear()
        
        self.graphics = [0, 0, 0, 0]
        self.graphics[self.active_option] = curses.A_REVERSE

        self.draw_menu(self.options, self.graphics)
        
        action = self.screen.getch()
        self.active_option = self.handle_menu_actions(self.active_option, action, self.graphics)
        self.handle_submit(self.active_option, action)

        self.screen.clear()


class SettingsMenu(Menu):

    def __init__(self, screen, _state: dict, _window: dict):
        super().__init__(screen, _window)

        self.state = _state
        self.active_option = 0

        self.graphics = [0, 0, 0, 0, 0]
        self.graphics[self.active_option] = curses.A_REVERSE
        self.load_settings()
    
    def load_settings(self, path: str = "settings.json") -> None:
        """ Simple function that loads the preset settings
        from a json called settings. If non exists creates one 
        with values from the config file
        
        :param path: path to the settings file 
        """
        settings_path = pathlib.Path(path).absolute()

        data: dict = {}
        if settings_path.exists() and settings_path.stat().st_size > 0:
            data = common.load_settings(path)
        else:
            common.write_settings(default_settings, path)
            data = default_settings

        self.settings: GameSettings = data

            
    def create_options(self):

        option_list = (
            f"Inital snake length: \t{self.settings['init_length']}", 
            f"Growth size: \t\t{self.settings['growth_size']}", 
            f"Speed: \t\t{self.settings['speed']}", 
            f"Acceleration: \t\t{self.settings['acceleration']}",
            "Back"
        )

        return option_list
        
    def handle_settings(self, action):
        """ Handles the user input to increment or decrement values

        could also be done with a step value witch is either -1 or 1 
        
        :param action: user key input
        """
        
        # Handle increment
        if action == curses.KEY_RIGHT:
            if self.active_option == 0:
                self.settings["init_length"] += 1

            elif self.active_option == 1:
                self.settings["growth_size"] += 1
            
            elif self.active_option == 2:
                self.settings["speed"] += 1

            elif self.active_option == 3:
                self.settings["acceleration"] += 1
            else: 
                return

        # Handle decrement (and prevent the value getting below 0)
        elif action == curses.KEY_LEFT:
            if self.active_option == 0:
                self.settings["init_length"] = max(self.settings["init_length"] -1, 0)

            elif self.active_option == 1:
                self.settings["growth_size"] = max(self.settings["growth_size"]- 1, 0)
            
            elif self.active_option == 2:
                self.settings["speed"] = max(self.settings["speed"] - 1, 0)

            elif self.active_option == 3:
                self.settings["acceleration"] = max(self.settings["acceleration"] - 1, 0)

            else: 
                return 
        # if key is not right or left
        else: 
            return

        # write the new settings 
        common.write_settings(self.settings)




    def handle_submit(self, action):
        if action == Keys.ENTER.value:
            if self.active_option == len(self.graphics) -1:
                self.update_state("MAIN")
                self.screen.clear()

    def __call__(self) -> None:

        # Main loop for the main Menu        
        self.graphics = [0,0,0,0,0]
        self.graphics[self.active_option] = curses.A_REVERSE
        
        _options = self.create_options()
        self.draw_menu(_options, self.graphics)
        
        action = self.screen.getch()
        self.active_option = self.handle_menu_actions(self.active_option, action, self.graphics)
        self.handle_settings(action)
        self.handle_submit(action)

        self.screen.clear()


