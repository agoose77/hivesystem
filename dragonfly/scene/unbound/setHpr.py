from bee import *
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class setHpr(worker):
    setHpr = Antenna("push", "Coordinate")
    entity = Antenna("pull", "id")
    b_entity = buffer("pull", "id")
    connect(entity, b_entity)
    hpr = variable("Coordinate")
    connect(setHpr, hpr)

    @modifier
    def do_setHpr(self):
        axis = self.get_entity(self.b_entity)
        axis.setHpr(self.hpr.x, self.hpr.y, self.hpr.z)
        axis.commit()

    trigger(hpr, b_entity)
    trigger(hpr, do_setHpr)

    def set_get_entity(self, get_entity):
        self.get_entity = get_entity

    def place(self):
        libcontext.socket(("get_entity", "NodePath"), socket_single_required(self.set_get_entity))
