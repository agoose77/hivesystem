from bee import *
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *

class setZ(worker):
  setZ = antenna("push", "float")
  z = variable("float")
  connect(setZ, z)
  @modifier
  def do_setz(self):
    axis = self.entity().get_proxy("AxisSystem")
    axis.origin.z = self.z
    axis.commit()
  trigger(z, do_setz)
  def set_entity(self, entity):
    self.entity = entity
  def place(self):
    libcontext.socket("entity", socket_single_required(self.set_entity))
