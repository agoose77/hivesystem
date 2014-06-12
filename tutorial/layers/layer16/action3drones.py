import somelibrary

import bee
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class animationmanager(bee.drone):
    def __init__(self):
        self.animations = {}

    def add_animation(self, identifier, animation):
        self.animations[identifier] = animation

    def play(self, identifier):
        animation = self.animations[identifier]
        somelibrary.play_animation(animation)

    def place(self):
        p = plugin_supplier(self.play)
        libcontext.plugin(("animation", "play"), p)
        p = plugin_supplier(self.add_animation)
        libcontext.plugin(("animation", "add"), p)


class soundmanager(bee.drone):
    def __init__(self):
        self.sounds = {}

    def add_sound(self, identifier, sound):
        self.sounds[identifier] = sound

    def play(self, identifier):
        sound = self.sounds[identifier]
        somelibrary.play_sound(sound)

    def place(self):
        p = plugin_supplier(self.play)
        libcontext.plugin(("sound", "play"), p)
        p = plugin_supplier(self.add_sound)
        libcontext.plugin(("sound", "add"), p)
    
