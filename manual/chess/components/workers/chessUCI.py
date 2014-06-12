import bee
from bee.segments import *
import libcontext
from libcontext.pluginclasses import *
from libcontext.socketclasses import *

from ..UCIChessEngine import UCIChessEngine

class chessUCI(bee.worker):
  player = variable("str")
  parameter(player)
  engine_binary = variable("str")
  parameter(engine_binary)
  engine_dir = variable("str")
  parameter(engine_dir,None)
    
  turn = antenna("pull","str")
  v_turn = buffer("pull","str")
  connect(turn, v_turn)
  trig_turn = triggerfunc(v_turn)
    
  make_move = antenna("push",("str","chess"))
  v_make_move = variable(("str","chess"))
  connect(make_move, v_make_move)
  @modifier
  def do_make_move(self):
    self.UCIengine.make_move(self.v_make_move)
    self.trig_turn()
  trigger(v_make_move, do_make_move, "update")
  
  get_move = output("push",("str","chess"))
  v_move = variable("str")
  t_move = transistor("str")
  connect(v_move, t_move)
  connect(t_move, get_move)
  trig_move = triggerfunc(t_move)
   
  trigger_get_move = antenna("push","trigger")
  @modifier
  def do_get_move(self):  
    self.trig_turn()
    if self.v_turn == self.player: 
      self.v_move = self.UCIengine.get_move()
      self.trig_move()
  trigger(trigger_get_move, do_get_move)
      
  def place(self):
    assert self.player in ("White", "Black")
    self.UCIengine = UCIChessEngine(self.engine_binary,self.engine_dir)

