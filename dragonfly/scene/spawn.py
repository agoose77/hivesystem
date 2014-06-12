import bee
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *

from .matrix import matrix

import Spyder
matrix0 = matrix(Spyder.AxisSystem(),"AxisSystem")

class spawn(bee.worker):
  entityclassname = antenna("pull", "id")
  b_entityclassname = buffer("pull", "id")
  connect(entityclassname, b_entityclassname)
  v_entityname = variable("id")
  v_matrix = variable(("object","matrix"))
  @modifier
  def do_spawn(self):
    self.spawnfunc(self.b_entityclassname, self.v_entityname)
    axis = self.v_matrix.get_copy("AxisSystem")
    ent = self.get_entity(self.v_entityname)
    ent.set_axissystem(axis)
    ent.commit()
  
  spawn_matrix = antenna("push",("id",("object","matrix")))
  uw = unweaver(("id",("object","matrix")), v_entityname, v_matrix)
  connect(spawn_matrix, uw)
  trigger(v_entityname, b_entityclassname, "input")    
  trigger(v_matrix, do_spawn, "input")

  spawn = antenna("push","id")
  b_spawn = buffer("push","id")
  @modifier
  def set_identity_matrix(self):
    self.v_matrix = matrix0
  connect(spawn, b_spawn)
  connect(b_spawn, v_entityname)
  trigger(b_spawn, set_identity_matrix, "input")
  trigger(b_spawn, b_spawn, "input")
  trigger(b_spawn, do_spawn, "input")
  
  def set_spawnfunc(self, spawnfunc):
    self.spawnfunc = spawnfunc
  def set_get_entity(self, get_entity):
    self.get_entity = get_entity
  def place(self):
    libcontext.socket(("get_entity", "AxisSystem"), socket_single_required(self.set_get_entity))
    libcontext.socket(("spawn","entity"), socket_single_required(self.set_spawnfunc))
