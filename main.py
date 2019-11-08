#!/usr/bin/env python3
import curses

from screen import Screen

def get_usage():
    return {"users":[
            ("player1", (0.3,1,2,81.2*1024**2), (0.9, 3,4,17.1*1024**2), "vpn0"),
            ("player2", (0.2,5,6,45.2*1024), (0.1, 7,8,2000), "vpn1")
            ],
            "vpn": [
            ("vpn0", (0.3, 1,2,81.2*1024**2), (0.8, 3,4,17.1*1024**2)),
            ("vpn1", (0.2, 5,6,45.2*1024), (0.1, 7,8,2000)),
            ("total", (0.5, 7,8,81.2*1024**2), (0.8,10,12,17.1*1024**2))
            ],
            }

def main(scr):
    screen = Screen(scr)
    curses.curs_set(0)
    while True:
        screen.draw_frame(get_usage())
        try:
            key = scr.getkey()
        except curses.error:
            key = None
        except KeyboardInterrupt:
            exit(0)

curses.wrapper(main)
