import bee
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *

class action3worker(bee.worker):
  def set_animplayfunc(self, animplayfunc):
    self.animplay = animplayfunc
  def set_soundplayfunc(self, soundplayfunc):
    self.soundplay = soundplayfunc
  def set_addanimfunc(self, addanimfunc):
    self.add_animation = addanimfunc
  def set_addsoundfunc(self, addsoundfunc):
    self.add_sound = addsoundfunc
  def _init(self):
    self.add_animation("swim", "splash-animation")
    self.add_sound("swim", "splash.wav")
    self.add_animation("crouch", "crouching")
    self.add_sound("crouch", "crouch.wav")  
  def place(self):    
    s = socket_single_required(self.set_animplayfunc)
    libcontext.socket(("animation", "play"), s)
    s = socket_single_required(self.set_soundplayfunc)
    libcontext.socket(("sound", "play"), s)

    s = socket_single_required(self.set_addanimfunc)
    libcontext.socket(("animation", "add"), s)
    s = socket_single_required(self.set_addsoundfunc)
    libcontext.socket(("sound", "add"), s)

    p = plugin_single_required(self._init)
    libcontext.plugin(("bee", "init"), p)

  animplay = antenna("push","id")
  v_anim = variable("id")
  connect(animplay, v_anim)    
  @modifier
  def do_animplay(self):
    self.animplay(self.v_anim)
  trigger(v_anim, do_animplay)

  soundplay = antenna("push","id")
  v_sound = variable("id")
  connect(soundplay, v_sound)  
  @modifier
  def do_soundplay(self):
    self.soundplay(self.v_sound)
  trigger(v_sound, do_soundplay)
