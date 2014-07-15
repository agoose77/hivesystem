from .drone import drone
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *
from .event import event as eventclass

import sys
import operator

python2 = (sys.version_info[0] == 2)

modes = ("all", "match", "leader", "match_leader", "head", "match_head", "trigger")


def func_cmp(func1, func2):
    f1, f2 = func1, func2
    if python2:
        f1, f2 = f1.im_func, f2.im_func
    if func1 != func2:
        return False
    if python2:
        b1 = hasattr(func1, "im_self")
        b2 = hasattr(func2, "im_self")
        if b1 != b2:
            return False
        if not b1:
            return True
        return func1.im_self is func2.im_self

    else:
        return func1 is func2


class eventhandler(drone):
    doexit = lambda self: False

    def __init__(self):
        self.listeners = []
        drone.__init__(self)
        self.nextevents = []
        self.lock = False
        self.raiser = True

    def read_exception(self, exception):
        self.read_event(exception.add_leader("exception"))

    def read_event(self, event):
        self.tick = None
        if event.match("tick"):
            self.tick = event

        for mode, callback, pattern, priority in list(self.listeners):
            self.lock = True

            if self.doexit() and event.match_head("stop") is None:
                break

            if event.processed:
                break

            if mode == "all":
                callback(event)

            if mode == "trigger":
                if event.match_leader(pattern) is not None:
                    callback()

            elif mode == "match":
                if event == pattern:
                    callback()

            elif mode == "leader":
                match = event.match_leader(pattern)
                if match is not None:
                    callback(match)
                    if match.processed:
                        event.processed = True

            elif mode == "match_leader":
                match = event.match_leader(pattern)
                if match is not None:
                    callback(event)

            elif mode == "head":
                match = event.match_head(pattern)
                if match is not None:
                    callback(match)
                    if match.processed:
                        event.processed = True

            elif mode == "match_head":
                match = event.match_head(pattern)
                if match is not None:
                    callback(event)

        self.process_next_events()
        self.lock = False

    def process_next_events(self):
        counter = 0
        while counter < len(self.nextevents):
            event, on_tick, currtick = self.nextevents[counter]
            if on_tick and (self.tick is None or currtick is self.tick):
                counter += 1
                continue
            self.nextevents.pop(counter)
            self.read_event(event)
            break

    def read_event_next(self, event, on_tick=False):
        self.nextevents.append((eventclass(event), on_tick, self.tick))
        if not self.lock:
            self.process_next_events(False)

    def read_event_next_tick(self, event):
        self.read_event_next(event, True)

    def listener(self, listener):
        # print("LISTENER", listener[0], listener[1])
        self.add_listener(*listener)

    def add_listener(self, mode, callback, pattern=None, priority=0):
        assert mode in modes, mode
        if mode != "all":
            assert pattern != None

        assert hasattr(callback, '__call__')
        listener = (mode, callback, pattern, priority)
        self.listeners.append(listener)
        self.listeners.sort(key=operator.itemgetter(3), reverse=True)
        return listener

    def remove_listener(self, listener):
        listeners = [l for l in self.listeners if l is listener]
        if not listeners:
            raise KeyError("Listener not found: %s" % (str(listener)))

        if len(listeners) > 1:
            raise KeyError("More than one listener: %s" % (str(listener)))

        self.listeners = [l for l in self.listeners if l is not listener]

    def set_doexit(self, doexit):
        self.doexit = doexit

    def eventhandler_lock(self):
        self.lock = True

    def eventhandler_unlock(self):
        self.lock = False
        self.raiser = True

    def raiser_activate(self):
        self.raiser = True

    def raiser_deactivate(self):
        self.raiser = False

    def place(self):
        libcontext.plugin(("evin", "event"), plugin_supplier(self.read_event))
        libcontext.plugin(("evin", "event", "next"), plugin_supplier(self.read_event_next))
        libcontext.plugin(("evin", "event", "next_tick"), plugin_supplier(self.read_event_next_tick))
        libcontext.plugin(("evin", "read-exception"), plugin_supplier(self.read_exception))
        libcontext.plugin(("evin", "add_listener"), plugin_supplier(self.add_listener))
        libcontext.plugin(("evin", "remove_listener"), plugin_supplier(self.remove_listener))
        libcontext.socket(("evin", "listener"), socket_container(self.listener))
        libcontext.socket(("doexit"), socket_single_optional(self.set_doexit))
        libcontext.plugin(("eventhandler", "lock"), plugin_supplier(self.eventhandler_lock))
        libcontext.plugin(("eventhandler", "unlock"), plugin_supplier(self.eventhandler_lock))
        libcontext.plugin(("eventhandler", "raiser", "active"), plugin_supplier(lambda: self.raiser))
        libcontext.plugin(("eventhandler", "raiser", "activate"), plugin_supplier(self.raiser_activate))
        libcontext.plugin(("eventhandler", "raiser", "deactivate"), plugin_supplier(self.raiser_deactivate))

