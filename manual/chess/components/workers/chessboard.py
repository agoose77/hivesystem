import bee
from bee.segments import *
import libcontext
from libcontext.pluginclasses import *
from libcontext.socketclasses import *

from .. import chessboard as comp_chessboard

class pandachessboard(comp_chessboard.chessboard):
  def __init__(self, boardparent):
    self.boardparent = boardparent
    comp_chessboard.chessboard.__init__(self)
  def move(self,move):
    self.boardparent.move(move)

class chessboard(bee.worker):
  player = variable("str")
  parameter(player,"Both")

  turn = antenna("pull","str")
  v_turn = buffer("pull","str")
  connect(turn, v_turn)
  trig_turn = triggerfunc(v_turn)
  
  make_move = antenna("push",("str","chess"))
  v_make_move = variable(("str","chess"))
  connect(make_move, v_make_move)
  @modifier
  def do_make_move(self):
    self.board.make_move(self.v_make_move)
  trigger(v_make_move, do_make_move, "update")
  
  get_move = output("push",("str","chess"))
  v_move = variable("str")
  t_move = transistor("str")
  connect(v_move, t_move)
  connect(t_move, get_move)
  trig_move = triggerfunc(t_move)
  
  def move(self, move):  
    try:
      self.eventhandler_lock()
      if self.player != "Both":
        self.trig_turn()
        if self.v_turn != self.player or self.player is None: raise ValueError
      self.v_move = move
      self.trig_move()
    finally:
      self.eventhandler_unlock()  
      
  def set_eventhandler_lock(self, eventhandler_lock):
    self.eventhandler_lock = eventhandler_lock
  def set_eventhandler_unlock(self, eventhandler_unlock):
    self.eventhandler_unlock = eventhandler_unlock
  def place(self):
    assert self.player in ("White", "Black", "Both", None)
    self.board = pandachessboard(self)

    libcontext.socket(("eventhandler","lock"), 
      socket_single_required(self.set_eventhandler_lock))
    
    libcontext.socket(("eventhandler","unlock"), 
      socket_single_required(self.set_eventhandler_unlock))
