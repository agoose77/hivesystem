"""
A pacemaker provides the following attributes:
- start_time: the time at the first tick
- time: the time at the last (current) tick
- ticks: the number of ticks passed (0 at the first tick)
"""

import libcontext, bee, time
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class pacemaker_simple(bee.drone):
    first = True

    def set_eventfunc(self, eventfunc):
        self.eventfunc = eventfunc

    def tick(self):
        t = time.time()
        if self.first:
            self.first = False
            self.ticks = 0
            self.start_time = t
            self.time = t
            self.eventfunc(bee.event("start"))

        self.eventfunc(bee.event("tick"))
        self.time = t
        self.ticks += 1

    def on_exit(self):
        self.eventfunc(bee.event("stop"))

    def place(self):
        libcontext.socket(("evin", "event"), socket_single_required(self.set_eventfunc))
        libcontext.plugin("pacemaker", plugin_supplier(self))
    
