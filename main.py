#!/usr/bin/env python3
import curses

import ipset

from screen import Screen

def get_usage():
    return {"users":[
            ("player1", (1,2,81.2*1024**2), (3,4,17.1*1024**2), "vpn0"),
            ("player2", (5,6,45.2*1024), (7,8,2000), "vpn1")
            ],
            "vpn": [
            ("vpn0", (1,2,81.2*1024**2), (3,4,17.1*1024**2)),
            ("vpn1", (5,6,45.2*1024), (7,8,2000)),
            ("total", (7,8,81.2*1024**2), (10,12,17.1*1024**2))
            ]
            }

def main(scr):
    screen = Screen(scr, None)
    curses.curs_set(0)
    while True:
        screen.draw_frame(get_usage())
        scr.getkey()

curses.wrapper(main)
