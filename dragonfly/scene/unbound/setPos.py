from bee import *
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *
from Spyder import Coordinate

class setPos(worker):
  setPos = antenna("push", "Coordinate")
  entity = antenna("pull", "id")
  b_entity = buffer("pull", "id")
  connect(entity, b_entity)
  pos = variable("Coordinate")
  connect(setPos, pos)
  @modifier
  def do_setPos(self):
    axis = self.get_entity(self.b_entity)
    axis.origin = Coordinate(self.pos.x, self.pos.y, self.pos.z)
    axis.commit()
  trigger(pos, b_entity)
  trigger(pos, do_setPos)
  def set_get_entity(self, get_entity):
    self.get_entity = get_entity
  def place(self):
    libcontext.socket(("get_entity", "AxisSystem"), socket_single_required(self.set_get_entity))
