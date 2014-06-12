import libcontext, libcontext.socketclasses, libcontext.pluginclasses
from ..drone import drone


class disconnect(drone):
    def __call__(self, source, target):
        if (source, target) not in self.pinconnect.connections:
            raise ValueError("Cannot disconnect pins: unknown connection")
        con = self.pinconnect.connections[source, target]
        del self.pinconnect.connections[source, target]
        if source.__pinmode__ == "push":
            source._remove_output(con)
        else:
            target._remove_input(con)

    def set_pinconnect(self, pinconnect):
        self.pinconnect = pinconnect

    def place(self):
        s = libcontext.socketclasses.socket_single_required(self.set_pinconnect)
        libcontext.socket(("pin", "connect"), s)
        p = libcontext.pluginclasses.plugin_supplier(self)
        libcontext.plugin(("pin", "disconnect"), p)
