import os
import platform
from window import Window


# curses does not run out the box in windows and some
# additional packages have to be installed
if platform.system() == 'win32':
    try:
        import curses
    except ImportError:
        os.system("pip install windows-curses")
        import curses
else:
    import curses

if __name__ == "__main__":

    # create window instance and run warpped around curses
    window = Window()
    curses.wrapper(window.run)
