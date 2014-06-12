import bee
from bee.segments import *

from .. import chesskeeper as comp_chesskeeper

class chesskeeper(bee.worker):
  gamekeeper = output("pull",("object","gamekeeper"))
  keeper = variable(("object","gamekeeper"))
  connect(keeper, gamekeeper)
  
  make_move = antenna("push",("str","chess"))
  v_make_move = variable("str")
  connect(make_move,v_make_move)
  
  @modifier
  def do_make_move(self):
    self.keeper.make_move(self.v_make_move)
  trigger(v_make_move, do_make_move)
  
  def place(self):
    self.keeper = comp_chesskeeper.chesskeeper().new()
