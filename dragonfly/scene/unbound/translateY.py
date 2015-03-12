from bee import *
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class translateY(worker):
    translateY = Antenna("push", "float")
    entity = Antenna("pull", "id")
    b_entity = buffer("pull", "id")
    connect(entity, b_entity)
    y = variable("float")
    connect(translateY, y)

    @modifier
    def do_transy(self):
        axis = self.get_entity(self.b_entity)
        axis.origin.y += self.y
        axis.commit()

    trigger(y, b_entity)
    trigger(y, do_transy)

    def set_get_entity(self, get_entity):
        self.get_entity = get_entity

    def place(self):
        libcontext.socket(("get_entity", "AxisSystem"), socket_single_required(self.set_get_entity))
