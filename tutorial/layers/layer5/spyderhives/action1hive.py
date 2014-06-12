import bee
from bee.spyderhive import spyderframe, SpyderMethod


def insert_sound_item(sounditem):
    initbee = bee.init("sounddict")
    initbee[sounditem.identifier] = sounditem.soundfile
    return initbee


def insert_animation_item(animationitem):
    initbee = bee.init("animdict")
    initbee[animationitem.identifier] = animationitem.animation
    return initbee


class action1hive(spyderframe):
    SpyderMethod("make_bee", "SoundItem", insert_sound_item)
    SpyderMethod("make_bee", "AnimationItem", insert_animation_item)
  
