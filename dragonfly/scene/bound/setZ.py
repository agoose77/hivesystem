from bee import *
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class setZ(worker):
    setZ = Antenna("push", "float")
    z = variable("float")
    connect(setZ, z)

    @modifier
    def do_setz(self):
        axis = self.get_matrix().get_proxy("AxisSystem")
        axis.origin.z = self.z
        axis.commit()

    trigger(z, do_setz)

    def set_get_matrix(self, function):
        self.get_matrix = function

    def place(self):
        libcontext.socket(("entity", "bound", "matrix"), socket_single_required(self.set_get_matrix))
