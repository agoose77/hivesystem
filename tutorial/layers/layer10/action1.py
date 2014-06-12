#translation of action1.hivemap into hive system Python code

#import configuration
from conf.action1hive import action1hive as action1hive_conf

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

  action1hive_conf = action1hive_conf (
    animdict = animdict,
    sounddict = sounddict,
  )

  animplay = antenna(animdict.inkey)
  soundplay = antenna(sounddict.inkey)

