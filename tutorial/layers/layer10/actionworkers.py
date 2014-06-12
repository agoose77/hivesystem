import bee
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *
  
import somelibrary
 
class play_animation(bee.worker):
  @modifier
  def do_play(self):
    somelibrary.play_animation(self.v_inp)
  
  inp = antenna('push', 'str')
  
  v_inp = variable('str')
  
  connect(inp, v_inp)
  trigger(v_inp, do_play)


class play_sound(bee.worker):
  @modifier
  def do_play(self):
    somelibrary.play_sound(self.v_inp)
  
  inp = antenna('push', 'str')
  
  v_inp = variable('str')
  
  connect(inp, v_inp)
  trigger(v_inp, do_play)


class action3_play_animation(bee.worker):
  
  def set_playfunc(self, playfunc):
    self.play = playfunc
  
  @modifier
  def do_play(self):
    self.play(self.v_inp)
  
  inp = antenna('push', 'id')
  
  v_inp = variable('id')
  
  trigger(v_inp, do_play)
  connect(inp, v_inp)
  
  def place(self):    
    s = socket_single_required(self.set_playfunc)
    libcontext.socket(("animation", "play"), s)


class action3_play_sound(bee.worker):
  
  def set_playfunc(self, playfunc):
    self.play = playfunc
  
  @modifier
  def do_play(self):
    self.play(self.v_inp)
  
  inp = antenna('push', 'id')
  
  v_inp = variable('id')
  
  trigger(v_inp, do_play)
  connect(inp, v_inp)
  
  def place(self):    
    s = socket_single_required(self.set_playfunc)
    libcontext.socket(("sound", "play"), s)
