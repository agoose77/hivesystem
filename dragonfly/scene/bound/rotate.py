from bee import *
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class rotateX(worker):
    rotate = antenna("push", "float")
    rotation = variable("float")
    connect(rotate, rotation)

    @modifier
    def do_rotate(self):
        axis = self.entity().get_proxy("AxisSystem")
        axis.rotateX(self.rotation)
        axis.commit()

    trigger(rotation, do_rotate)

    def set_entity(self, entity):
        self.entity = entity

    def place(self):
        libcontext.socket("entity", socket_single_required(self.set_entity))


class rotateY(worker):
    rotate = antenna("push", "float")
    rotation = variable("float")
    connect(rotate, rotation)

    @modifier
    def do_rotate(self):
        axis = self.entity().get_proxy("AxisSystem")
        axis.rotateY(self.rotation)
        axis.commit()

    trigger(rotation, do_rotate)

    def set_entity(self, entity):
        self.entity = entity

    def place(self):
        libcontext.socket("entity", socket_single_required(self.set_entity))


class rotateZ(worker):
    rotate = antenna("push", "float")
    rotation = variable("float")
    connect(rotate, rotation)

    @modifier
    def do_rotate(self):
        axis = self.entity().get_proxy("AxisSystem")
        axis.rotateZ(self.rotation)
        axis.commit()

    trigger(rotation, do_rotate)

    def set_entity(self, entity):
        self.entity = entity

    def place(self):
        libcontext.socket("entity", socket_single_required(self.set_entity))
