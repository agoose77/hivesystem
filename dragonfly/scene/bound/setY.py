from bee import *
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class setY(worker):
    setY = Antenna("push", "float")
    y = variable("float")
    connect(setY, y)

    @modifier
    def do_sety(self):
        axis = self.get_matrix().get_proxy("AxisSystem")
        axis.origin.y = self.y
        axis.commit()

    trigger(y, do_sety)

    def set_get_matrix(self, function):
        self.get_matrix = function

    def place(self):
        libcontext.socket(("entity", "bound", "matrix"), socket_single_required(self.set_get_matrix))
