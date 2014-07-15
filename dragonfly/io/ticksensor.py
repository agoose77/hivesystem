import bee
from bee.segments import *
import libcontext
from libcontext.pluginclasses import *
from libcontext.socketclasses import *


class ticksensor(bee.worker):
    start = antenna("push", "trigger")
    stop = antenna("push", "trigger")

    on = variable("bool")
    parameter(on, True)

    outp = output("push", "trigger")
    trig_outp = triggerfunc(outp)

    @modifier
    def m_start(self):
        if self.listener is not None: return
        self.listener = self.add_listener("trigger", self.trig_outp, "tick", priority=1)
        self.on = True

    trigger(start, m_start)

    @modifier
    def m_stop(self):
        if self.on:
            self.remove_listener(self.listener)
        self.listener = None
        self.on = False

    trigger(stop, m_stop)

    def set_add_listener(self, add_listener):
        self.add_listener = add_listener

    def set_remove_listener(self, remove_listener):
        self.remove_listener = remove_listener

    def place(self):
        libcontext.socket(("evin", "add_listener"), socket_single_required(self.set_add_listener))
        libcontext.socket(("evin", "remove_listener"), socket_single_required(self.set_remove_listener))
        self.listener = None
        if self.on:
            libcontext.plugin(("bee", "init"), plugin_single_required(self.m_start))
