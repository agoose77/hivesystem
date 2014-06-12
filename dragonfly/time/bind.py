import libcontext
from bee.bind import *
import bee.event


class tickforwarder_evin(binderdrone):
    def __init__(self):
        self.bindnames = set()
        self.send_event = {}
        self.first = {}

    def listener(self, event):
        for bindname in list(self.bindnames):
            if bindname not in self.binderworker.hives:
                self.bindnames.remove(bindname)
                continue
            if self.first[bindname]:
                self.first[bindname] = False
                self.send_event[bindname](bee.event("start"))
            self.send_event[bindname](event)

    def set_send_event(self, send_event):
        self.send_event[self.currbindname] = send_event

    def bind(self, binderworker, bindname):
        self.binderworker = binderworker
        binderworker.eventfuncs.append(self.listener)
        self.bindnames.add(bindname)
        self.first[bindname] = True
        self.currbindname = bindname
        s = libcontext.socketclasses.socket_single_required(self.set_send_event)
        libcontext.socket(("evin", "event"), s)

    def place(self):
        p = libcontext.pluginclasses.plugin_single_required(("match_leader", self.listener, "tick"))
        libcontext.plugin(("evin", "listener"), p)


class bind(bind_baseclass):
    bind_pacemaker = bindparameter("transmit")
    binder("bind_pacemaker", "transmit", pluginbridge("pacemaker"))
    # TODO: binder("bind_pacemaker", "simple")
    transmit_tick = bindparameter("evin")
    binder("transmit_tick", False, None)
    binder("transmit_tick", "evin", tickforwarder_evin(), "bindname")
    #TODO: binder("transmit_tick", "pacemaker", tickforwarder_pacemaker(), "bindname") TODO in case of separate pacemaker


# NOTE: pacemaker must generate a start event on first use

#note the difference between:
# 1. having the same pacemaker+tick pause (time workers get not updated, but catch up)
# 2. having different pacemakers+tick pause (tick time workers do not catch up; time workers do, unless you control the pacemaker's
#  time as well, TODO)
