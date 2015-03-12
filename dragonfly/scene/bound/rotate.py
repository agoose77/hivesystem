from bee import *
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class rotateX(worker):
    rotate = Antenna("push", "float")
    rotation = variable("float")
    connect(rotate, rotation)

    @modifier
    def do_rotate(self):
        axis = self.get_matrix().get_proxy("AxisSystem")
        axis.rotateX(self.rotation)
        axis.commit()

    trigger(rotation, do_rotate)

    def set_get_matrix(self, function):
        self.get_matrix = function

    def place(self):
        libcontext.socket(("entity", "bound", "matrix"), socket_single_required(self.set_get_matrix))


class rotateY(worker):
    rotate = Antenna("push", "float")
    rotation = variable("float")
    connect(rotate, rotation)

    @modifier
    def do_rotate(self):
        axis = self.get_matrix().get_proxy("AxisSystem")
        axis.rotateY(self.rotation)
        axis.commit()

    trigger(rotation, do_rotate)

    def set_get_matrix(self, function):
        self.get_matrix = function

    def place(self):
        libcontext.socket(("entity", "bound", "matrix"), socket_single_required(self.set_get_matrix))


class rotateZ(worker):
    rotate = Antenna("push", "float")
    rotation = variable("float")
    connect(rotate, rotation)

    @modifier
    def do_rotate(self):
        axis = self.get_matrix().get_proxy("AxisSystem")
        axis.rotateZ(self.rotation)
        axis.commit()

    trigger(rotation, do_rotate)

    def set_get_matrix(self, function):
        self.get_matrix = function

    def place(self):
        libcontext.socket(("entity", "bound", "matrix"), socket_single_required(self.set_get_matrix))
