# import custom data model
import spyder, Spyder
import characteraction
from Spyder import CharacterAction

#import workers
from actionworkers import play_animation
from actionworkers import play_sound

#define action3 hive
import bee
from dragonfly.std import *
import dragonfly.logic
import dragonfly.blocks
from bee import antenna, connect


class action2hive(bee.frame):
    actiondict = dragonfly.logic.dictionary("CharacterAction")()
    actionplay = antenna(actiondict.inkey)

    action = dragonfly.blocks.block("CharacterAction")()
    set_action = dragonfly.blocks.setter("CharacterAction")()
    connect(set_action, action)
    connect(actiondict.outvalue, set_action._set)

    get_action = dragonfly.blocks.getter("CharacterAction")()
    connect(action, get_action)

    transistor_2 = transistor("str")()
    transistor_3 = transistor("str")()
    connect(get_action.animation, transistor_2)
    connect(get_action.soundfile, transistor_3)
    connect(set_action.on_set, transistor_2)
    connect(set_action.on_set, transistor_3)

    play_animation = play_animation()
    play_sound = play_sound()
    connect(transistor_2, play_animation)
    connect(transistor_3, play_sound)

    d = bee.init("actiondict")
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


