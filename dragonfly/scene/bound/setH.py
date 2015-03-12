from bee import *
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class setH(worker):
    setH = Antenna("push", "float")
    h = variable("float")
    connect(setH, h)

    @modifier
    def do_setH(self):
        axis = self.get_matrix().get_proxy("NodePath")
        axis.setH(self.h)
        axis.commit()

    trigger(h, do_setH)

    def set_get_matrix(self, function):
        self.get_matrix = function

    def place(self):
        libcontext.socket(("entity", "bound", "matrix"), socket_single_required(self.set_get_matrix))
