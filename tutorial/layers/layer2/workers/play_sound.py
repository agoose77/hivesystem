import bee
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *
  
import somelibrary


class play_sound(bee.worker):
  @modifier
  def do_play(self):
    somelibrary.play_sound(self.v_inp)
  
  inp = antenna('push', 'str')
  
  v_inp = variable('str')
  
  connect(inp, v_inp)
  trigger(v_inp, do_play)
  
