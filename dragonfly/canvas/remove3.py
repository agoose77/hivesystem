import bee
from bee.segments import *
import libcontext
from libcontext.socketclasses import *

class remove3(bee.worker):
  trig = antenna("push", "trigger")  
  identifier = variable("id")
  parameter(identifier)
  @modifier
  def do_remove(self):
    for remover in self.removers:
      processed = remover(self.identifier)
      if processed: break      
  trigger(trig, do_remove) 
     
  def add_remover(self, remover):
    self.removers.append(remover)
  def place(self):
    self.removers = []
    s = socket_container(self.add_remover)
    libcontext.socket(("canvas", "remove1"), s)
