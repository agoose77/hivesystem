import bee
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *
  
import somelibrary

class action1worker(bee.worker):
  def place(self):    
    adict = {}
    sdict = {}
    adict["walk"] = "walk-animation"
    sdict["walk"] = "walking.wav"

    adict["jump"] = "jump-animation"
    sdict["jump"] = "jmp.wav"
    self.animdict = adict
    self.sounddict = sdict

  animplay = antenna("push","id")
  v_anim = variable("id")
  connect(animplay, v_anim)    
  @modifier
  def do_animplay(self):
    anim = self.animdict[self.v_anim]
    somelibrary.play_animation(anim)
  trigger(v_anim, do_animplay)

  soundplay = antenna("push","id")
  v_sound = variable("id")
  connect(soundplay, v_sound)  
  @modifier
  def do_soundplay(self):
    sound = self.sounddict[self.v_sound]
    somelibrary.play_sound(sound)
  trigger(v_sound, do_soundplay)

