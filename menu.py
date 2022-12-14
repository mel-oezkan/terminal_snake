import curses

from typing import List, Tuple

import common

from config import Defaults
from config import GameSettings
from config import Modes 
from config import Keys 
from config import default_settings

class Menu:
    def __init__(self, screen, _window) -> None:
        """ Constructor for the 
        
        param: screen (_CursesWindow): The screen instance of curses
        param: _window: Information on which winodw is active (e.g. GAME or MENU)
        """

        self.screen = screen
        self.screen.nodelay(Modes.MENU.value)
        self.window_state = _window

        # create a state value to track which menu item is selected
        self.menu_state = {"active_menu": "MAIN"}
        

    def update_window(self, value) -> None:
        """Function to change the value of the window state (changes value within window clas)

        :param value: value of the new window state 
        """

        self.window_state["active_window"] = value


    def draw_menu(self, menu_options: Tuple[str], graphics: Tuple[int]) -> None:
        """ Generic function that plots the given menu opitons
        according to the given graphics. (Graphics handles how
        the items are drawn)

        :param menu_options: Items to be displayed
        :param graphics: How the items are displayed (e.g attributes such as color)
        """
        
        # check if the two objects are same length
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


    def handle_menu_actions(self, active_opt: int, action: int, graphics: List[int]) -> None:
        """ Function that handles the up and down arrow keys 
        and handles the selected option respectively

        :param active_opt: value of the active option
        :param action: ascii-value of the pressed key
        """
        
        if action == curses.KEY_UP:
            return (active_opt - 1) % len(graphics)
        
        elif action == curses.KEY_DOWN:
            return (active_opt + 1) % len(graphics)
        
        return active_opt


    def update_state(self, value) -> None:
        """ Update the Menu state
        
        :param value: name of the new menu state
        """
        self.state["active_menu"] = value

    
    def __call__(self) -> None:
        
        main_menu = MainMenu(self.screen, self.menu_state, self.window_state)
        settings_menu = SettingsMenu(self.screen, self.menu_state, self.window_state)
        leaderboard_menu = ScoresMenu(self.screen, self.menu_state, self.window_state)

        while True:
            if self.menu_state["active_menu"] == "MAIN":
                # self.graphics[self.active_option] = curses.A_REVERSE
                main_menu()
                
            elif self.menu_state["active_menu"] == "SETTINGS":
                settings_menu()

            elif self.menu_state["active_menu"] == "SCORES":
                leaderboard_menu()

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
                raise NotImplementedError



class MainMenu(Menu):
    options = ("Play", "Settings", "Scores", "Exit")
    
    def __init__(self, screen, _state: dict, _window: dict) -> None:
        """ Initalize class variables
        
        :param screen (_CursesScreen): cureses screen instance
        :param _state: which game subwindow is active
        :param _window: which main window is active (currently: GAME)
        :param _status: information about score
        """
        super().__init__(screen, _window)

        self.state = _state 
        self.active_option = 0

        self.graphics = [0, 0, 0, 0]
        self.graphics[self.active_option] = curses.A_REVERSE


    def handle_submit(self, active_option, action) -> None:
        """ Function to handle if the enter key is clicked
        where each option innvokes different updated
        
        :param action: ascii value of pressed key
        """
        if action == Keys.ENTER.value:

            if active_option == 0:
                self.update_state("GAME")
                self.screen.refresh()

            elif active_option == 1:
                self.update_state("SETTINGS")
                self.screen.clear()

            elif active_option == 2:
                self.update_state("SCORES")
                self.screen.clear()

            elif active_option == 3:
                self.update_state("QUIT")
                self.screen.clear()


    def __call__(self) -> None:
        # Main loop for the main Menu        
        self.screen.clear()
        
        # set variables for drawing
        self.graphics = [0, 0, 0, 0]
        self.graphics[self.active_option] = curses.A_REVERSE
        self.draw_menu(self.options, self.graphics)
        
        # handle key inputs
        action = self.screen.getch()
        self.active_option = self.handle_menu_actions(self.active_option, action, self.graphics)
        self.handle_submit(self.active_option, action)

        self.screen.clear()



class SettingsMenu(Menu):
    def __init__(self, screen, _state: dict, _window: dict) -> None:
        """ Initalize class variables
        
        :param screen (_CursesScreen): cureses screen instance
        :param _state: which game subwindow is active
        :param _window: which main window is active (currently: GAME)
        :param _status: information about score
        """
        super().__init__(screen, _window)
        
        self.state = _state
        self.active_option = 0

        self.graphics = [0,0,0,0,0,0]
        self.graphics[self.active_option] = curses.A_REVERSE
        self.load_settings()
    

    def load_settings(self) -> None:
        """ Simple function that loads the preset settings
        from a json called settings. If non exists creates one 
        with values from the config file
        """

        data: dict = {}
        data = common.load_settings()

        if not data:
            common.write_settings(default_settings)
            data = default_settings

        self.settings: GameSettings = data

            
    def create_options(self) -> None:
        """ Given the settings (dict) creates string representations
        for each of the items
        """

        option_list = (
            f"Inital snake length: \t\t{self.settings['init_length']}", 
            f"Growth size: \t\t{self.settings['growth_size']}", 
            f"Speed: \t\t\t{self.settings['speed']}", 
            f"Acceleration: \t\t{self.settings['acceleration']}",
            f"Food count: \t\t{self.settings['food_count']}",
            "Back"
        )

        return option_list
        

    def handle_settings(self, action) -> None: 
        """ Handles the user input to increment or decrement values 
        and updates the values within the settings file

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

            elif self.active_option == 4:
                self.settings["food_count"] += 1
            
            else: 
                return

        # Handle decrement (and prevent the value getting below 0)
        elif action == curses.KEY_LEFT:
            if self.active_option == 0:
                self.settings["init_length"] = max(self.settings["init_length"] -1, 4)

            elif self.active_option == 1:
                self.settings["growth_size"] = max(self.settings["growth_size"]- 1, 1)
            
            elif self.active_option == 2:
                self.settings["speed"] = max(self.settings["speed"] - 1, 1)

            elif self.active_option == 3:
                self.settings["acceleration"] = max(self.settings["acceleration"] - 1, 1)

            elif self.active_option == 4:
                self.settings["food_count"] = max(self.settings["food_count"] - 1, 1)

            else: 
                return 
        # if key is not right or left
        else: 
            return

        # write the new settings 
        common.write_settings(self.settings)


    def handle_submit(self, action: int) -> None:
        """ Handles a enter key press 
        
        Given that the last option is selected which will always be the 
        return option. The current menu will change into the MAIN window

        :param action: ascii value of pressed input key
        """

        if action == Keys.ENTER.value:
            if self.active_option == len(self.graphics) -1:
                self.update_state("MAIN")
                self.screen.clear()

    def __call__(self) -> None:

        # Main loop for the main Menu        
        self.graphics = [0,0,0,0,0,0]
        self.graphics[self.active_option] = curses.A_REVERSE
        
        _options = self.create_options()
        self.draw_menu(_options, self.graphics)

        # get user inputs and handle them
        action = self.screen.getch()
        self.active_option = self.handle_menu_actions(
            self.active_option, action, self.graphics
        )
        
        self.handle_settings(action)
        self.handle_submit(action)

        self.screen.clear()


class ScoresMenu(Menu):
    
    def __init__(self, screen, _state: dict, _window: dict):
        """ Initalize class variables
        
        :param screen (_CursesScreen): cureses screen instance
        :param _state: which game subwindow is active
        :param _window: which main window is active (currently: GAME)
        :param _status: information about score
        """
        super().__init__(screen, _window)

        self.state = _state

    def load_leaderboard(self):
        """ Loads the leaderboard from its file"""

        # reduce the leaderboard to top 5
        leaderboard_items = common.read_leaderboard()
        if len(leaderboard_items) > 5:
            leaderboard_items = leaderboard_items[:5] 

        # convert leaderboard items to str
        leaderboard_str = [
            f"{item['time']}: \t\t{item['score']}" for item in leaderboard_items
        ]

        # add Back button
        self.options = leaderboard_str if leaderboard_str else []
        self.options.append("Back")


    def handle_submit(self, action) -> None:
        """ Handles a enter key press 
        
        Given that the last option is selected which will always be the 
        return option. The current menu will change into the MAIN window

        :param action: ascii value of pressed input key
        """
        

        if action == Keys.ENTER.value:
            self.update_state("MAIN")
            self.screen.clear()
            return True

        return False


    def __call__(self) -> None:
        """ Main loop for the leaderboard window"""

        # load leaderboard and set up drawing variable
        self.load_leaderboard()
        self.graphics = [0 for _ in range(len(self.options))]
        self.graphics[-1] = curses.A_REVERSE

        # draw leaderboard
        self.draw_menu(self.options, self.graphics)
        
        # listen for the keys
        while True:
            action = self.screen.getch()
            if self.handle_submit(action):
                break
        
        self.screen.clear()
        
