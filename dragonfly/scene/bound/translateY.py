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
    axis = self.entity().get_proxy("AxisSystem")
    axis.origin.y += self.y
    axis.commit()
  trigger(y, do_transy)
  def set_entity(self, entity):
    self.entity = entity
  def place(self):
    libcontext.socket("entity", socket_single_required(self.set_entity))
