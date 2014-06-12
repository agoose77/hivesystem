from bee import *
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *
from Spyder import Coordinate


class setPos(worker):
    setPos = antenna("push", "Coordinate")
    pos = variable("Coordinate")
    connect(setPos, pos)

    @modifier
    def do_setPos(self):
        axis = self.entity().get_proxy("AxisSystem")
        axis.origin = Coordinate(self.pos.x, self.pos.y, self.pos.z)
        axis.commit()

    trigger(pos, do_setPos)

    def set_entity(self, entity):
        self.entity = entity

    def place(self):
        libcontext.socket("entity", socket_single_required(self.set_entity))
