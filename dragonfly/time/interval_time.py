import bee
from bee.segments import *

import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class interval_time(bee.worker):
    time = variable(("float", "quantity"))
    startvalue(time, 0)
    parameter(time, 0)

    start = antenna("push", "trigger")
    pause = antenna("push", "trigger")
    stop = antenna("push", "trigger")
    set_time = antenna("push", ("float", "quantity"))

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

    prev = variable(("float", "quantity"))
    startvalue(prev, 0)

    reach_end = output("push", "trigger")
    trigger_reach_end = triggerfunc(reach_end)

    def get_dif(self):
        time = self.pacemaker.time
        return time - self.prev

    def set_prev(self):
        self.prev = self.pacemaker.time

    def update_value(self):
        dif = self.get_dif() / self.time
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

        if self.time <= 0:
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

    v_set_time = variable(("float", "quantity"))
    connect(set_time, v_set_time)

    @modifier
    def m_set_time(self):
        if self.v_running: raise ValueError("Interval worker is running, cannot change time")
        if self.v_paused: raise ValueError("Interval worker is paused, cannot change time")
        self.time = self.v_set_time

    trigger(v_set_time, m_set_time)

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
