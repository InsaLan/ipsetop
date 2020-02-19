#!/usr/bin/env python3
import curses
import sys

from screen import Screen
from importer import Importer
from api import run_api


import time

def show_help():
    print("""
ipsetop: mesure bandwidth usage using ipsets
usage : ipsetop [args] <interface> [interface...]
args :
    -h show this help.
    -d run with a rest api on 1312 and disable tui. This does not run ipsetop in daemon.
    -r reverse interface direction.

api :
    all request should be made to /
    filtering and grouping can be done via parameters
    groupe by source ip and port : /?group-by=sip,port
    filter only https traffic to 1.1.1.1 : /?filter=dip:1.1.1.1,port:tcp:443
    note : this is different from /?filter=dip:1.1.1.1&filter=port:tcp:443
    which show both everything https and everything going to 1.1.1.1
    """)

def daemon(interfaces, reverse=False):
    importer = Importer(interfaces, reverse, "daemon")
    try:
        run_api(importer)
    except KeyboardInterrupt:
        pass
    importer.ipset.delete()
        
    

def tui(scr):
    screen = Screen(scr)

    importer = Importer()
    curses.curs_set(0)
    while True:
        screen.draw_frame(importer.get_data())
        try:
            key = scr.getkey()
            # TODO handle keys
            if key in "123":
                importer.update_sort(time=key)
            if key in "ud":
                importer.update_sort(dire=key)
        except curses.error:
            key = None
        except KeyboardInterrupt:
            exit(0)

if __name__ == "__main__":
    if "-h" in sys.argv:
        show_help()
    elif "-d" in sys.argv:
        args = sys.argv[1:]
        args.remove("-d")
        reverse = "-r" in args
        if reverse:
            args.remove("-r")
        daemon(args, reverse)
    else:
        curses.wrapper(tui)

