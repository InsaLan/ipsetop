#!/usr/bin/env python3
import curses

import ipset

def get_usage():
    return [
            ("player1", 81.2*1024**2, 17.1*1024**2),
            ("player2", 45.2*1024, 2000)
            ]

def unit(val):
    if val >= 1024**2*10:
        return "{:.1f}mb".format(val/1024**2)
    elif val >= 1024*10:
        return "{:.1f}kb".format(val/1024)
    else:
        return "{:.1f} b".format(val)

def pad(val, count, char=" "):
    if count > 0:
        return val + char*(count - len(val))
    else:
        return char*(-count - len(val)) + val

def printline(scr, line=0, pre="", post="", frac=0):
    y,x = scr.getmaxyx()
    pos = int(frac*x)

    content = pad(pre, x-len(post)) + post
    scr.addstr(line, 0, content[:pos], curses.A_REVERSE)
    scr.addstr(line, pos, content[pos:])

def print_header(scr,max_val=100*1024**2):
    _,m = scr.getmaxyx()
    unit_line = ""
    line = "└"
    for i in range(1,6):
        l = int(m/5*i)
        unit_line += pad(unit(max_val/5*i), len(unit_line)-l)
        line += pad("┴", len(line)-l, "─")
    scr.addstr(0, 0, unit_line)
    scr.addstr(1, 0, line)

    return 2

def print_footer(scr):
    y,x = scr.getmaxyx()
    return y

def print_content(scr, start, end):
    max_bw = 100*1024**2
    for i,(name, down, up) in enumerate(get_usage()):
        printline(scr, i*2+start, "<= " + name, unit(down), down/max_bw)
        printline(scr, i*2+1+start, "=>", unit(up), up/max_bw)


def print_frame(scr):
    """
    ┌─┬─┐
    ├│┼│┤
    └─┴─┘
    """
    start = print_header(scr)
    end = print_footer(scr)
    print_content(scr, start, end)


def main(scr):
    scr.clear()
    print_frame(scr)
    scr.refresh()
    scr.getkey()

curses.wrapper(main)
