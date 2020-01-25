#!/usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    from ipset import Ipset,Entry
except ModuleNotFoundError:
    from .ipset import Ipset,Entry
import os
from time import time
import re

class Net:
    def __init__(self, interface="tun+"):
        self.id = id
        self.interface = interface
        self.ipset = Ipset("ipsetop-" + interface)
        self.reverse = Ipset("ipsetop-reverse-" + interface)
        self.ipset.create("hash:ip,port,ip", skbinfo=False, comment=False)
        self.reverse.create("hash:ip,port,ip", skbinfo=False, comment=False)
        self.logs = list()
        for cmd in self.generate_iptables(stop = True):
            while os.system(cmd) == 0:
                pass
        for cmd in self.generate_iptables():
            os.system(cmd)


    def generate_iptables(self, stop = False):
        verb = "-D" if stop else "-I"
        return ["iptables {0} POSTROUTING -t mangle -o {1} -m set ! --match-set ipsetop-{1} src,dst,dst -j SET --add-set ipsetop-{1} src,dst,dst".format(verb, self.interface),
        "iptables {0} PREROUTING -t mangle -i {1} -m set ! --match-set ipsetop-{1} dst,src,src -j SET --add-set ipsetop-reverse-{1} dst,src,src".format(verb, self.interface)]


    def clear(self):
        self.ipset.flush()
        self.reverse.flush()


    def get_all_flows(self):
        entries = self.ipset.list().entries
        users = dict()
        for entry in entries:
            elem = entry.elem
            up = entry.bytes or 0
            source, destination, port =  elem.split(",")
            users[elem] = Flow(source, destination, port, up=up)

        rev_entries = self.reverse.list().entries
        for entry in rev_entries:
            if entry.elem in users:
                users[entry.elem].down = entry.bytes or 0

        return users

    def delete(self):
        for cmd in self.generate_iptables(stop=True):
            os.system(cmd)
        self.ipset.destroy()
        self.reverse.destroy()


class Flow:
    def __init__(self, source, destination, port, up=0, down=0):
        self.source = source
        self.destination = destination
        self.port = port
        self.up = up
        self.down = down

    def to_dict(self):
        return {
            "source": self.source,
            "destination": self.destination,
            "port": self.port,
            "up": self.up,
            "down": self.down,
        }
