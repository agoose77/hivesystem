from __future__ import print_function

import bee
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class maindrone(bee.drone):
    def keypress(self, key):
        if key == "W":
            i = "walk"
            self.action1_anim(i)
            self.action1_sound(i)
        elif key == "TAB":
            i = "jump"
            self.action1_anim(i)
            self.action1_sound(i)
        elif key == "R":
            self.action2_play("run")
        elif key == "SPACE":
            self.action2_play("shoot")
        elif key == "S":
            i = "swim"
            self.action3_anim(i)
            self.action3_sound(i)
        elif key == "C":
            i = "crouch"
            self.action3_anim(i)
            self.action3_sound(i)

    def start(self):
        print("START")

    def set_action1_anim(self, func):
        self.action1_anim = func

    def set_action1_sound(self, func):
        self.action1_sound = func

    def set_action2_play(self, func):
        self.action2_play = func

    def set_action3_anim(self, func):
        self.action3_anim = func

    def set_action3_sound(self, func):
        self.action3_sound = func

    def place(self):
        s = socket_single_required(self.set_action1_anim)
        libcontext.socket(("action1", "play", "animation"), s)
        s = socket_single_required(self.set_action1_sound)
        libcontext.socket(("action1", "play", "sound"), s)

        s = socket_single_required(self.set_action2_play)
        libcontext.socket(("action2", "play", "action"), s)

        s = socket_single_required(self.set_action3_anim)
        libcontext.socket(("action3", "play", "animation"), s)
        s = socket_single_required(self.set_action3_sound)
        libcontext.socket(("action3", "play", "sound"), s)
  

  
