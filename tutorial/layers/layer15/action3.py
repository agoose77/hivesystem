import bee
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *

class action3drone(bee.drone):
  def __init__(self):
    self._initialized = False
    
  def set_animplayfunc(self, animplayfunc):
    self.animplay = animplayfunc
  def set_soundplayfunc(self, soundplayfunc):
    self.soundplay = soundplayfunc
  def set_addanimfunc(self, addanimfunc):
    self.add_animation = addanimfunc
  def set_addsoundfunc(self, addsoundfunc):
    self.add_sound = addsoundfunc
            
  def _init(self):
    if self._initialized: return
    self.add_animation("swim", "splash-animation")
    self.add_sound("swim", "splash.wav")
    self.add_animation("crouch", "crouching")
    self.add_sound("crouch", "crouch.wav")  
    self._initialized = True
    
  def do_animplay(self, anim):
    self._init()
    self.animplay(anim)
  def do_soundplay(self, sound):
    self._init()
    self.soundplay(sound)

  def place(self):  
    #plugins received from the managers
    s = socket_single_required(self.set_animplayfunc)
    libcontext.socket(("animation", "play"), s)
    s = socket_single_required(self.set_soundplayfunc)
    libcontext.socket(("sound", "play"), s)

    s = socket_single_required(self.set_addanimfunc)
    libcontext.socket(("animation", "add"), s)
    s = socket_single_required(self.set_addsoundfunc)
    libcontext.socket(("sound", "add"), s)
    
    #plugins provided to the main drone
    p = plugin_supplier(self.do_animplay)
    libcontext.plugin(("action3", "play", "animation"), p)
    p = plugin_supplier(self.do_soundplay)
    libcontext.plugin(("action3", "play", "sound"), p)

