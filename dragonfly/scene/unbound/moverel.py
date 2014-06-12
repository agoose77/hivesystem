
from bee import *
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


def get_worker(name, xyz): 
  class moverel(worker):
    """
    Relative movement along %s axis
    """ % xyz
    __beename__ = name
    moverel = antenna("push", "float")
    movement = variable("float")
    connect(moverel, movement)

    entity = antenna("pull", "id")
    b_entity = buffer("pull", "id")
    connect(entity, b_entity)  

    @modifier
    def do_move(self):
      axis = self.get_entity(self.b_entity)
      axis.origin += getattr(axis, xyz) * self.movement
      axis.commit()
    trigger(movement, b_entity)    
    trigger(movement, do_move)
    def set_get_entity(self, get_entity):
      self.get_entity = get_entity
    def place(self):
      libcontext.socket(("get_entity", "AxisSystem"), socket_single_required(self.set_get_entity))
  return moverel
    
moverelX = get_worker("moverelX", "x")
moverelY = get_worker("moverelY", "y")
moverelZ = get_worker("moverelZ", "z")

