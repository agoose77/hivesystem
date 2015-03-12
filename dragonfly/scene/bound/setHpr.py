from bee import *
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class setHpr(worker):
    setHpr = Antenna("push", "Coordinate")
    hpr = variable("Coordinate")
    connect(setHpr, hpr)

    @modifier
    def do_setHpr(self):
        axis = self.get_matrix().get_proxy("NodePath")
        axis.setHpr(self.hpr.x, self.hpr.y, self.hpr.z)
        axis.commit()

    trigger(hpr, do_setHpr)

    def set_get_matrix(self, function):
        self.get_matrix = function

    def place(self):
        libcontext.socket(("entity", "bound", "matrix"), socket_single_required(self.set_get_matrix))
