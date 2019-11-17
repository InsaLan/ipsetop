#!/usr/bin/env python3
import curses

from screen import Screen
from importer import Importer

def main(scr):
    screen = Screen(scr)

    importer = Importer()
    curses.curs_set(0)
    while True:
        screen.draw_frame(importer.get_data())
        try:
            key = scr.getkey()
            # TODO handle keys
        except curses.error:
            key = None
        except KeyboardInterrupt:
            exit(0)

curses.wrapper(main)
