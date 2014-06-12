#import workers
from actionworkers import play_animation
from actionworkers import play_sound

#define action1 hive
import bee
from dragonfly.std import *
import dragonfly.logic
from bee import antenna, connect

class action1hive(bee.frame):
 
  animdict = dragonfly.logic.dictionary("str")()
  play_animation = play_animation()
  connect(animdict.outvalue, play_animation)
  

  sounddict = dragonfly.logic.dictionary("str")() 
  play_sound = play_sound()
  connect(sounddict.outvalue, play_sound)

  adict = bee.init(animdict)
  sdict = bee.init(sounddict)

  adict["walk"] = "walk-animation"
  sdict["walk"] = "walking.wav"

  adict["jump"] = "jump-animation"
  sdict["jump"] = "jmp.wav"

  animplay = antenna(animdict.inkey)
  soundplay = antenna(sounddict.inkey)

