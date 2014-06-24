import bee
from bee.segments import *

import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class interval_ticks(bee.worker):
    ticks = variable("int")
    startvalue(ticks, 0)
    parameter(ticks, 0)

    start = antenna("push", "trigger")
    pause = antenna("push", "trigger")
    stop = antenna("push", "trigger")
    set_ticks = antenna("push", "int")

    v_value = variable(("float", "fraction"))
    startvalue(v_value, 0)
    v_running = variable("bool")
    startvalue(v_running, False)
    v_paused = variable("bool")
    startvalue(v_paused, False)

    value = output("pull", ("float", "fraction"))
    connect(v_value, value)
    running = output("pull", "bool")
    connect(v_running, running)
    paused = output("pull", "bool")
    connect(v_paused, paused)

    prev = variable("int")
    startvalue(prev, 0)

    reach_end = output("push", "trigger")
    trigger_reach_end = triggerfunc(reach_end)

    def get_dif(self):
        ticks = self.pacemaker.ticks
        return ticks - self.prev  # In principle, 1

    def set_prev(self):
        self.prev = self.pacemaker.ticks

    def update_value(self):
        dif = self.get_dif() / float(self.ticks)
        newvalue = self.v_value + dif
        if newvalue >= 1:
            self.m_pause()
            self.v_paused = False
            newvalue = 1.0
            self.trigger_reach_end()
        self.v_value = newvalue
        self.set_prev()

    @modifier
    def m_start(self):
        if self.v_running:
            return

        if self.ticks <= 0:
            self.v_value = 1.0
            self.v_running = False
            return

        self.set_prev()
        if self.v_paused:
            self.v_paused = False
        else:
            self.v_value = 0
        self.v_running = True
        self.listener = self.add_listener("trigger", self.update_value, "tick", priority=2)

    @modifier
    def m_pause(self):
        if self.v_running:
            self.remove_listener(self.listener)
        self.v_running = False
        self.v_paused = True

    @modifier
    def m_stop(self):
        self.m_pause()
        self.v_paused = False
        self.v_value = 0

    trigger(start, m_start)
    trigger(pause, m_pause)
    trigger(stop, m_stop)

    v_set_ticks = variable("int")
    connect(set_ticks, v_set_ticks)

    @modifier
    def m_set_ticks(self):
        if self.v_running:
            raise ValueError("Interval worker is running, cannot change ticks")
        if self.v_paused:
            raise ValueError("Interval worker is paused, cannot change ticks")
        self.ticks = self.v_set_ticks

    trigger(v_set_ticks, m_set_ticks)

    def set_pacemaker(self, pacemaker):
        self.pacemaker = pacemaker

    def set_add_listener(self, add_listener):
        self.add_listener = add_listener

    def set_remove_listener(self, remove_listener):
        self.remove_listener = remove_listener

    def place(self):
        libcontext.socket("pacemaker", socket_single_required(self.set_pacemaker))
        libcontext.socket(("evin", "add_listener"), socket_single_required(self.set_add_listener))
        libcontext.socket(("evin", "remove_listener"), socket_single_required(self.set_remove_listener))
