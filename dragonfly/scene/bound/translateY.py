from bee import *
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class translateY(worker):
    translateY = antenna("push", "float")
    y = variable("float")
    connect(translateY, y)

    @modifier
    def do_transy(self):
        axis = self.get_matrix().get_proxy("AxisSystem")
        axis.origin.y += self.y
        axis.commit()

    trigger(y, do_transy)

    def set_get_matrix(self, function):
        self.get_matrix = function

    def place(self):
        libcontext.socket(("entity", "bound", "matrix"), socket_single_required(self.set_get_matrix))
