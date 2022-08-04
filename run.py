
import sys
from window import Window
import os
import platform


# curses does not run out the box in windows and some
# additional packages have to be installed
if platform.system() == 'win32':
    try:
        import curses
    except Exception as e:
        os.system("pip install windows-curses")
        import curses

import curses


if __name__ == "__main__":
    window = Window()

    curses.wrapper(window.run)
