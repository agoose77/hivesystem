from bee import *
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *

class animation(worker):
  loop = antenna("push", "trigger")
  stop = antenna("push", "trigger")
  @modifier
  def m_loop(self):
    self.actor().animate(self.v_animation_name,loop=True)
  animation_name = antenna("pull", "str")
  t_animation_name = transistor("str")
  v_animation_name = variable("str")
  connect(animation_name, t_animation_name)
  connect(t_animation_name, v_animation_name)
  trigger(loop, t_animation_name)
  trigger(loop, m_loop)
  @modifier
  def m_stop(self):
    self.actor().stop()
  trigger(stop, m_stop)   
  def set_actor(self, actor):
    self.actor = actor
  def place(self):
    libcontext.socket("actor", socket_single_required(self.set_actor))
    
