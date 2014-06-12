from bee import *
import libcontext
from libcontext.pluginclasses import *
from libcontext.socketclasses import *

class keyboardmove(drone):
  def __init__(self, player):
    assert player in ("White", "Black")
    self.player = player
    self.moveprocessors = []
  def move(self, event):
    if self.turn() != self.player: return
    if len(event) != 1: return
    event.processed = True
    move = event[0]    
    for f in self.moveprocessors: f(move)
  def add_moveprocessor(self, moveprocessor):
    self.moveprocessors.append(moveprocessor)
  def set_turn(self, turn_func):
    self.turn = turn_func
  def place(self):    
    s = socket_single_required(self.set_turn)
    libcontext.socket(("game","turn"), s)
  
    s = socket_container(self.add_moveprocessor)
    libcontext.socket(("game","process_move"), s)

    listener = plugin_single_required(("leader", self.move, "command"))
    libcontext.plugin(("evin", "listener"), listener)
