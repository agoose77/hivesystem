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
        axis = self.get_matrix().get_proxy("AxisSystem")
        axis.origin = Coordinate(self.pos.x, self.pos.y, self.pos.z)
        axis.commit()

    trigger(pos, do_setPos)

    def set_get_matrix(self, function):
        self.get_matrix = function

    def place(self):
        libcontext.socket(("entity", "bound", "matrix"), socket_single_required(self.set_get_matrix))
