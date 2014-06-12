#translation of action1.hivemap into hive system Python code

#import configuration Spyder hive
from spyderhives.action1conf import action1conf

#import workers
from workers.play_animation import play_animation
from workers.play_sound import play_sound

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

  action1conf = action1conf (
    animdict = animdict,
    sounddict = sounddict,
  )

  animplay = antenna(animdict.inkey)
  soundplay = antenna(sounddict.inkey)

