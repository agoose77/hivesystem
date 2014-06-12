# import custom data model
import spyder, Spyder
import characteraction
from Spyder import CharacterAction

import bee
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *

import somelibrary


class action2drone(bee.drone):
    def __init__(self):
        d = {}
        d["run"] = CharacterAction(
            animation="running.animation",
            soundfile="run.wav",
        )
        #or: d["run"] = CharacterAction("running.animation", "run.wav")

        d["shoot"] = CharacterAction(
            animation="shooting.animation",
            soundfile="shoot.wav",
        )
        #or: d["shoot"] = CharacterAction("shooting.animation", "shoot.wav")

        self.actiondict = d

    def actionplay(self, id_action):
        action = self.actiondict[id_action]
        somelibrary.play_animation(action.animation)
        somelibrary.play_sound(action.soundfile)

    def place(self):
        p = plugin_supplier(self)
        libcontext.plugin("action2", p)
