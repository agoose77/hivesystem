import bee
import libcontext
from bee.segments import *

class parent(bee.worker):
  entityname = antenna("pull", "id")
  entityparentname = antenna("pull", "id")
  w = weaver(("id","id"), entityname, entityparentname)
  names = buffer("pull",("id","id"))
  connect(w,names)
  
  @modifier
  def m_parent(self):
    self.entity_parent_to(self.names[0],self.names[1])
  parent = antenna("push","trigger")  
  trigger(parent, names) 
  trigger(parent, m_parent)

  def set_entity_parent_to(self,entity_parent_to):
    self.entity_parent_to = entity_parent_to
  
  def place(self):
    s = libcontext.socketclasses.socket_single_required(self.set_entity_parent_to)
    libcontext.socket(("entity","parent_to"), s)
