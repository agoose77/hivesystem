from bee import *
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class setHpr(worker):
    setHpr = antenna("push", "Coordinate")
    hpr = variable("Coordinate")
    connect(setHpr, hpr)

    @modifier
    def do_setHpr(self):
        axis = self.entity().get_proxy("NodePath")
        axis.setHpr(self.hpr.x, self.hpr.y, self.hpr.z)
        axis.commit()

    trigger(hpr, do_setHpr)

    def set_entity(self, entity):
        self.entity = entity

    def place(self):
        libcontext.socket("entity", socket_single_required(self.set_entity))
