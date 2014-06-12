import bee
from bee.segments import *
import libcontext

class remove_actor_or_entity(bee.worker):
  inp = antenna("push","id")
  v_inp = variable("id")
  connect(inp, v_inp)
  @modifier
  def m_remove(self):
    try:
      self.remove_actor(self.v_inp)
    except KeyError:
      self.remove_entity(self.v_inp)
  trigger(v_inp, m_remove)
  
  def set_remove_actor(self, remove_actor):
    self.remove_actor = remove_actor
  def set_remove_entity(self, remove_entity):
    self.remove_entity = remove_entity    
  def place(self):
    s = libcontext.socketclasses.socket_single_required(self.set_remove_actor)
    libcontext.socket(("remove","actor"), s)
    s = libcontext.socketclasses.socket_single_required(self.set_remove_entity)
    libcontext.socket(("remove","entity"), s)
