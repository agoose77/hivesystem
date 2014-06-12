import bee
from bee.segments import *
import libcontext
from libcontext.socketclasses import *

class update4(bee.worker):
  identifier = variable("id")
  parameter(identifier)

  @modifier
  def do_update2(self):
    for updater in self.updaters:
      processed = updater(self.identifier, self.v_bbox)
      if processed: break
    else:
      raise ValueError("Unknown identifier %s" % self.identifier)
  bbox = antenna("push",("object", "box2d"))
  v_bbox = variable(("object", "box2d"))
  connect(bbox, v_bbox)
  trigger(v_bbox, do_update2) 

  @modifier
  def do_update3(self):
    for updater in self.updaters:
      processed = updater(self.identifier, self.v_params)
      if processed: break
    else:
      raise ValueError("Unknown identifier %s" % self.identifier)
  params = antenna("push",("object", "general"))
  v_params = variable(("object", "general"))
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
