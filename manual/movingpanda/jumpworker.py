import bee
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class jumpworker(bee.worker):
    start = antenna("push", "trigger")

    height = variable("float")
    parameter(height)
    duration = variable("float")
    parameter(duration)
    position = variable("float")
    startvalue(position, 0)

    @modifier
    def jump(self):
        if self.position != 0: return
        self.time = self.pacemaker.time
        self.listener = self.add_listener("trigger", self.update, "tick")

    trigger(start, jump)

    def update(self):
        progress = (self.pacemaker.time - self.time) / self.duration

        avgvelocity = 4 * self.height * (1 - progress)
        self.position = progress * avgvelocity
        if self.position < 0:
            self.remove_listener(self.listener)
            self.position = 0

        mat = self.entity().get_proxy("AxisSystem")
        mat.origin.z = self.position
        mat.commit()


    def set_pacemaker(self, pacemaker):
        self.pacemaker = pacemaker

    def set_entity(self, entity):
        self.entity = entity

    def set_add_listener(self, add_listener):
        self.add_listener = add_listener

    def set_remove_listener(self, remove_listener):
        self.remove_listener = remove_listener

    def place(self):
        libcontext.socket("pacemaker", socket_single_required(self.set_pacemaker))
        libcontext.socket(("evin", "add_listener"), socket_single_required(self.set_add_listener))
        libcontext.socket(("evin", "remove_listener"), socket_single_required(self.set_remove_listener))
        libcontext.socket("entity", socket_single_required(self.set_entity))
