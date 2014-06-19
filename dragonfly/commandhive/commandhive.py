from __future__ import print_function
import time

import bee
from bee import hivemodule, event

import libcontext
from libcontext.pluginclasses import *
from libcontext.socketclasses import *

from .inputhandler import inputhandler as inputhandler_class


class inputhandlerhive(bee.frame):
    inputhandler_class()


class commandapp(bee.drone):
    def __init__(self):
        self.startupfunctions = []
        self.cleanupfunctions = []
        self.doexit = False
        self._commands = []
        self._eventreaders = []

    def add_eventreader(self, eventreader):
        self._eventreaders.append(eventreader)

    def on_tick(self):
        pass

    def run(self):
        try:
            self.finished = False
            for f in self.startupfunctions: f()
            while not self.doexit:
                self.pacemaker.tick()
                self.on_tick()
                time.sleep(0.005)
                comnr = 0
                while comnr < len(self._commands):
                    com = self._commands[comnr]
                    comnr += 1
                    for e in self._eventreaders:
                        e(event("command", com))
                        self.pacemaker.tick()
                        self.on_tick()
                        time.sleep(0.005)
                self._commands = []

        finally:
            self.cleanup()

    def exit(self):
        self.doexit = True

    def addstartupfunction(self, startupfunction):
        assert hasattr(startupfunction, "__call__")
        self.startupfunctions.append(startupfunction)

    def addcleanupfunction(self, cleanupfunction):
        assert hasattr(cleanupfunction, "__call__")
        self.cleanupfunctions.append(cleanupfunction)

    def cleanup(self):
        if self.finished == False:
            for f in self.cleanupfunctions: f()
        self.finished = True

    def new_command(self, command):
        self._commands.append(command)

    def display(self, arg):
        print(arg)

    def watch(self, *args):
        for a in args: print(a, end="")
        print()

    def set_pacemaker(self, pacemaker):
        self.pacemaker = pacemaker

    def place(self):
        libcontext.plugin(("command", "new_command"), plugin_supplier(self.new_command))
        libcontext.socket("startupfunction", socket_container(self.addstartupfunction))
        libcontext.socket("cleanupfunction", socket_container(self.addcleanupfunction))
        libcontext.plugin("exit", plugin_supplier(self.exit))
        libcontext.plugin("stop", plugin_supplier(self.exit))
        libcontext.plugin("display", plugin_supplier(self.display))
        libcontext.plugin("watch", plugin_supplier(self.watch))
        libcontext.socket("pacemaker", socket_single_required(self.set_pacemaker))
        libcontext.socket(("evin", "event"), socket_container(self.add_eventreader))
        libcontext.plugin("doexit", plugin_supplier(lambda: self.doexit))


from bee import connect
from ..time import simplescheduler
from ..sys import exitactuator
from ..event import sensor_match, sensor_leader
from ..time import pacemaker_simple


class commandhive_exit(bee.drone):
    def __init__(self, pattern):
        self.pattern = pattern

    def doexit(self):
        self.exitfunc()

    def set_exitfunc(self, exitfunc):
        self.exitfunc = exitfunc

    def place(self):
        listener = plugin_single_required(("match", self.doexit, self.pattern))
        libcontext.plugin(("evin", "listener"), listener)
        libcontext.socket("exit", socket_single_required(self.set_exitfunc))


class commandhive(bee.inithive):
    _hivecontext = hivemodule.appcontext(commandapp)
    inputhandler = inputhandlerhive()
    connect(("inputhandler", "evout"), "evin")
    scheduler = simplescheduler()
    exitactuator = exitactuator()
    cmdsensor_exit = commandhive_exit(("command", "exit"))
    cmdsensor_quit = commandhive_exit(("command", "quit"))

    pacemaker = pacemaker_simple()
  
