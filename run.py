import curses
from window import Window


if __name__ == "__main__":
    window = Window()
    curses.wrapper(window.run)
