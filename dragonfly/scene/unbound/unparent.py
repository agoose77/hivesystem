import bee
import libcontext
from bee.segments import *

class unparent(bee.worker):
  entityname = antenna("pull", "id")
  name = buffer("pull", "id")
  connect(entityname,name)
  
  @modifier
  def m_unparent(self):
    self.entity_unparent(self.name)
  unparent = antenna("push","trigger")  
  trigger(unparent, name) 
  trigger(unparent, m_unparent)

  def set_entity_unparent(self,entity_unparent):
    self.entity_unparent = entity_unparent
  
  def place(self):
    s = libcontext.socketclasses.socket_single_required(self.set_entity_unparent)
    libcontext.socket(("entity","unparent"), s)
