import bee
from bee.segments import *
import libcontext
from libcontext.socketclasses import *

inptype1 = ("id", ("object", "box2d"))
inptype2 = ("id", ("object", "general"))

class update2(bee.worker):
  @modifier
  def do_update2(self):
    identifier, bbox = self.v_bbox
    for updater in self.updaters:
      processed = updater(identifier, bbox)
      if processed: break
    else:
      raise ValueError("Unknown identifier %s" % self.identifier)
  bbox = antenna("push",inptype1)
  v_bbox = variable(inptype1)
  connect(bbox, v_bbox)
  trigger(v_bbox, do_update2) 

  @modifier
  def do_update3(self):
    identifier, parameters = self.v_params
    for updater in self.updaters:
      processed = updater(identifier, parameters)
      if processed: break
    else:
      raise ValueError("Unknown identifier %s" % self.identifier)
  params = antenna("push",inptype2)
  v_params = variable(inptype2)
  connect(params, v_params)
  trigger(v_params, do_update3) 
  
  def add_updater2(self, updater):
    self.updaters2.append(updater)
  def add_updater3(self, updater):
    self.updaters3.append(updater)
  def place(self):
    self.updaters2 = []
    self.updaters3 = []
    libcontext.socket(("canvas", "update2"), socket_container(self.add_updater2))
    libcontext.socket(("canvas", "update3"), socket_container(self.add_updater3))
