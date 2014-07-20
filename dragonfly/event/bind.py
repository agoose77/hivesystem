import libcontext
from bee.bind import *


class eventdispatcher(binderdrone):

    def __init__(self):
        self.bindnames = set()

    def listener(self, event):
        # As this is a plugin, it may be prematurely called
        if not self.bindnames:
            return

        event_forwarders = self.binderworker.event_handlers
        handler_states = self.binderworker.handler_states

        # Careful this list doesn't change during iteration
        for bindname in list(self.bindnames):
            if bindname not in self.binderworker.hives:
                self.bindnames.remove(bindname)
                continue

            # Check if this bind name is active
            is_active = handler_states[bindname]
            if not is_active:
                continue

            # Check we match the event
            event_after = event.match_head(bindname)
            if event_after is None:
                continue

            # Forward the event
            event_func = event_forwarders[bindname]
            event_func(event_after)

    def bind(self, binderworker, bindname):
        self.binderworker = binderworker

        # In case any other binders want event functions
        # Register this bind_class (which belongs to the hive BINDER only once)
        if self.listener not in binderworker.eventfuncs:
            binderworker.eventfuncs.append(self.listener)

        # So we know which processes exist
        self.bindnames.add(bindname)

        # Individual event handler of the BOUND class (multiple bound hives possible)
        def set_handler(func):
            binderworker.event_handlers[bindname] = func
            # Active state
            binderworker.handler_states[bindname] = True

        s = libcontext.socketclasses.socket_single_required(set_handler)
        libcontext.socket(("evin", "event"), s)

    def place(self):
        p = libcontext.pluginclasses.plugin_single_required(("all", self.listener))
        libcontext.plugin(("evin", "listener"), p)


class eventforwarder(eventdispatcher):

    def listener(self, event):
        # As this is a plugin, it may be prematurely called
        if not self.bindnames:
            return

        event_forwarders = self.binderworker.event_handlers
        handler_states = self.binderworker.handler_states

        # Careful this list doesn't change during iteration
        for bindname in list(self.bindnames):
            if bindname not in self.binderworker.hives:
                self.bindnames.remove(bindname)
                continue

            # Check if this bind name is active
            is_active = handler_states[bindname]
            if not is_active:
                continue

            # Forward the event
            event_func = event_forwarders[bindname]
            event_func(event)


class eventlistener(eventforwarder):

    def __init__(self, leader):
        self.bindnames = set()
        self.leader = leader

    def place(self):
        p = libcontext.pluginclasses.plugin_single_required(("match_leader", self.listener, self.leader))
        libcontext.plugin(("evin", "listener"), p)


class bind(bind_baseclass):
    dispatch_events = bindparameter("byhead")
    binder("dispatch_events", "byhead", eventdispatcher(), "bindname")
    binder("dispatch_events", "toall", eventforwarder(), "bindname")
