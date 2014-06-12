from bee import *
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *

class setH(worker):
  setH = antenna("push", "float")
  h = variable("float")
  connect(setH, h)
  @modifier
  def do_setH(self):
    axis = self.entity().get_proxy("NodePath")
    axis.setH(self.h)
    axis.commit()
  trigger(h, do_setH)
  def set_entity(self, entity):
    self.entity = entity
  def place(self):
    libcontext.socket("entity", socket_single_required(self.set_entity))
