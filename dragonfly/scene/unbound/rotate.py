from bee import *
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class rotateX(worker):
    rotate = antenna("push", "float")
    rotation = variable("float")
    connect(rotate, rotation)

    entity = antenna("pull", "id")
    b_entity = buffer("pull", "id")
    connect(entity, b_entity)

    @modifier
    def do_rotate(self):
        axis = self.get_entity(self.b_entity)
        axis.rotateX(self.rotation)
        axis.commit()

    trigger(rotation, b_entity)
    trigger(rotation, do_rotate)

    def set_get_entity(self, get_entity):
        self.get_entity = get_entity

    def place(self):
        libcontext.socket(("get_entity", "AxisSystem"), socket_single_required(self.set_get_entity))


class rotateY(worker):
    rotate = antenna("push", "float")
    rotation = variable("float")
    connect(rotate, rotation)

    entity = antenna("pull", "id")
    b_entity = buffer("pull", "id")
    connect(entity, b_entity)

    @modifier
    def do_rotate(self):
        axis = self.get_entity(self.b_entity)
        axis.rotateY(self.rotation)
        axis.commit()

    trigger(rotation, b_entity)
    trigger(rotation, do_rotate)

    def set_get_entity(self, get_entity):
        self.get_entity = get_entity

    def place(self):
        libcontext.socket(("get_entity", "AxisSystem"), socket_single_required(self.set_get_entity))


class rotateZ(worker):
    rotate = antenna("push", "float")
    rotation = variable("float")
    connect(rotate, rotation)

    entity = antenna("pull", "id")
    b_entity = buffer("pull", "id")
    connect(entity, b_entity)

    @modifier
    def do_rotate(self):
        axis = self.get_entity(self.b_entity)
        axis.rotateZ(self.rotation)
        axis.commit()

    trigger(rotation, b_entity)
    trigger(rotation, do_rotate)

    def set_get_entity(self, get_entity):
        self.get_entity = get_entity

    def place(self):
        libcontext.socket(("get_entity", "AxisSystem"), socket_single_required(self.set_get_entity))
