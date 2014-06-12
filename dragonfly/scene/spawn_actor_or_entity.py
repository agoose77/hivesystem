import bee
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *

from .matrix import matrix

import Spyder
matrix0 = matrix(Spyder.AxisSystem(),"AxisSystem")

class spawn_actor_or_entity(bee.worker):
  actorclassname = antenna("pull", "id")
  b_actorclassname = buffer("pull", "id")
  connect(actorclassname, b_actorclassname)
  v_actorname = variable("id")
  v_matrix = variable(("object","matrix"))
  @modifier
  def do_spawn(self):
    try:
      self.actorspawnfunc(self.b_actorclassname, self.v_actorname)
    except KeyError:
      self.entspawnfunc(self.b_actorclassname, self.v_actorname)
    axis = self.v_matrix.get_copy("AxisSystem")
    ent = self.get_entity(self.v_actorname)
    ent.set_axissystem(axis)
    ent.commit()
  
  spawn_matrix = antenna("push",("id",("object","matrix")))
  uw = unweaver(("id",("object","matrix")), v_actorname, v_matrix)
  connect(spawn_matrix, uw)
  trigger(v_actorname, b_actorclassname, "input")    
  trigger(v_matrix, do_spawn, "input")

  spawn = antenna("push","id")
  b_spawn = buffer("push","id")
  @modifier
  def set_identity_matrix(self):
    self.v_matrix = matrix0
  connect(spawn, b_spawn)
  connect(b_spawn, v_actorname)
  trigger(b_spawn, set_identity_matrix, "input")
  trigger(b_spawn, b_spawn, "input")
  trigger(b_spawn, do_spawn, "input")
  
  def set_actorspawnfunc(self, spawnfunc):
    self.actorspawnfunc = spawnfunc
  def set_entspawnfunc(self, spawnfunc):
    self.entspawnfunc = spawnfunc    
  def set_get_entity(self, get_entity):
    self.get_entity = get_entity
  def place(self):
    libcontext.socket(("get_entity", "AxisSystem"), socket_single_required(self.set_get_entity))
    libcontext.socket(("spawn","actor"), socket_single_required(self.set_actorspawnfunc))
    libcontext.socket(("spawn","entity"), socket_single_required(self.set_entspawnfunc))
    
