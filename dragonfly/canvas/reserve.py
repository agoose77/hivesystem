import bee
from bee.segments import *
import libcontext
from libcontext.socketclasses import *

inptype = ("id", ("object", "box2d"))
class reserve(bee.worker):
  inp = antenna("push", inptype)  
  v_inp = variable(inptype)
  connect(inp, v_inp)
  @modifier
  def do_reserve(self):
    id, bbox = self.v_inp
    for reserver in self.reservers:
      reserver(id, box=bbox)
  trigger(v_inp, do_reserve) 
     
  def add_reserver(self, reserver):
    self.reservers.append(reserver)
  def place(self):
    self.reservers = []
    s = socket_container(self.add_reserver)
    libcontext.socket(("canvas", "dynamic-reserve"), s)
