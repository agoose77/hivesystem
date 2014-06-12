import bee
from bee.spyderhive import spyderframe, SpyderMethod

def insert_sound_item(sounditem):
  initbee = bee.init("soundmanager")
  initbee.add_sound(sounditem.identifier, sounditem.soundfile)
  return initbee

def insert_animation_item(animationitem):
  initbee = bee.init("animationmanager")
  initbee.add_animation(animationitem.identifier, animationitem.animation)
  return initbee

class action3hive(spyderframe):
  SpyderMethod("make_bee", "SoundItem", insert_sound_item)
  SpyderMethod("make_bee", "AnimationItem", insert_animation_item)
  
