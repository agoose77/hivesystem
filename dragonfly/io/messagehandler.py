import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class messagehandler(bee.drone):

    """Manages messages handling (publish and subscribe)"""

    def __init__(self):
        self._bound_handlers = {}
        self._unbound_handlers = set()

        self._pending_messages = []

    def set_read_event(self, read_event):
        self.read_event = read_event

    def update(self):
        for process_name, subject, body in self._pending_messages:
            if process_name:
                try:
                    message_handlers = self._bound_handlers[process_name]

                except KeyError:
                    return

            else:
                message_handlers = self._unbound_handlers

            for handler in message_handlers:
                handler(subject, body)

        self._pending_messages.clear()

    def publish(self, process_name, subject, body):
        self._pending_messages.append((process_name, subject, body))

    def unsubscribe(self, handler, process_name=None):
        if process_name is not None:
            self._bound_handlers[process_name].remove(handler)

        self._unbound_handlers.remove(handler)

    def subscribe(self, handler, process_name=None):
        if process_name is not None:
            self._bound_handlers.setdefault(process_name, set()).add(handler)

        self._unbound_handlers.add(handler)

    def enable(self):
        self.add_listener("trigger", self.update, "tick", priority=10)

    def set_add_listener(self, add_listener):
        self.add_listener = add_listener

    def place(self):
        libcontext.plugin(("message", "subscribe"), plugin_supplier(self.subscribe))
        libcontext.plugin(("message", "unsubscribe"), plugin_supplier(self.unsubscribe))
        libcontext.plugin(("message", "publish"), plugin_supplier(self.publish))

        #Make sure we are enabled at startup
        libcontext.socket(("evin", "add_listener"), socket_single_required(self.set_add_listener))
        libcontext.plugin(("bee", "init"), plugin_single_required(self.enable))
