import bee
from bee.segments import *
import libcontext
from libcontext.socketclasses import *


class update3(bee.worker):
    identifier = variable("id")
    parameter(identifier)

    @modifier
    def do_update(self):
        for updater in self.updaters:
            processed = updater(self.identifier)
            if processed: break
        else:
            raise ValueError("Unknown identifier %s" % self.identifier)

    update = antenna("push", "trigger")
    trigger(update, do_update)

    def add_updater(self, updater):
        self.updaters.append(updater)

    def place(self):
        self.updaters = []
        libcontext.socket(("canvas", "update1"), socket_container(self.add_updater))
