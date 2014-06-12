import bee
import libcontext
from bee.segments import *

class show(bee.worker):
  show = antenna("push","trigger")
  entity = antenna("pull", "id")
  b_entity = buffer("pull", "id")
  connect(entity,b_entity)
  trigger(show, b_entity)
  @modifier
  def do_show(self):
    self.show(self.b_entity)
  trigger(show, do_show)
  def set_show(self, show):
    self.show = show
  def place(self):
    s = libcontext.socketclasses.socket_single_required(self.set_show)
    libcontext.socket(("entity","show"), s)
    
