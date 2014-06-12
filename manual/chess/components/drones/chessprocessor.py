from bee import *
import libcontext
from libcontext.pluginclasses import *
from libcontext.socketclasses import *

class chessprocessor(drone):
  def __init__(self):
    self.make_move_funcs = [] 
    self.turn = "White"
  def set_is_finished(self,is_finished_func):
    self.is_finished = is_finished_func
  def set_format_move(self,format_move_func):
    self.format_move = format_move_func
  def set_exit(self,exit_func):
    self.exit = exit_func
  def add_make_move(self, make_move_func):
    self.make_move_funcs.append(make_move_func)
  def process_move(self, move):
    move = self.format_move(move)
    for f in self.make_move_funcs: f(move)
    if self.is_finished(): self.exit()
    if self.turn == "White": self.turn = "Black"
    else: self.turn = "White"
  def place(self):
    s = socket_single_required(self.set_is_finished) 
    libcontext.socket(("game", "finished"),s)
    
    s = socket_single_required(self.set_format_move) 
    libcontext.socket(("game", "format_move"),s)
    
    s = socket_single_required(self.set_exit) 
    libcontext.socket("exit",s)

    s = socket_container(self.add_make_move) 
    libcontext.socket(("game","make_move"),s)
    
    p = plugin_supplier(self.process_move) 
    libcontext.plugin(("game", "process_move"),p)

    p = plugin_supplier(lambda: getattr(self, "turn")) 
    libcontext.plugin(("game", "turn"),p)
