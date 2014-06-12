from bee import *
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *

class translateX(worker):
  translateX = antenna("push", "float")
  entity = antenna("pull", "id")
  b_entity = buffer("pull", "id")
  connect(entity, b_entity)
  x = variable("float")
  connect(translateX, x)
  @modifier
  def do_transx(self):
    axis = self.get_entity(self.b_entity)
    axis.origin.x += self.x
    axis.commit()
  trigger(x, b_entity)
  trigger(x, do_transx)
  def set_get_entity(self, get_entity):
    self.get_entity = get_entity
  def place(self):
    libcontext.socket(("get_entity", "AxisSystem"), socket_single_required(self.set_get_entity))
