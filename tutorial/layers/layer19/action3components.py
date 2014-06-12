import somelibrary

class animationmanager(object):
  def __init__(self):
    self.animations = {}
  def add_animation(self, identifier, animation):
    self.animations[identifier] = animation
  def play(self, identifier):
    animation = self.animations[identifier]
    somelibrary.play_animation(animation)
        
class soundmanager(object):
  def __init__(self):
    self.sounds = {}
  def add_sound(self, identifier, sound):
    self.sounds[identifier] = sound
  def play(self, identifier):
    sound = self.sounds[identifier]
    somelibrary.play_sound(sound)    
