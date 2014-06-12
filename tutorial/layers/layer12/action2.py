# import custom data model
import spyder, Spyder
import characteraction
from Spyder import CharacterAction

import bee
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *

import somelibrary


class action2worker(bee.worker):
    def place(self):
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

    actionplay = antenna("push", "id")
    v_action = variable("id")
    connect(actionplay, v_action)

    @modifier
    def do_play(self):
        action = self.actiondict[self.v_action]
        somelibrary.play_animation(action.animation)
        somelibrary.play_sound(action.soundfile)

    trigger(v_action, do_play)
  


