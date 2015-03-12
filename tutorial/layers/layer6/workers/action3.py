# translation of action3.hivemap into hive system Python code

#find out where the spydermaps are
import os
import spydermaps

spydermapsdir = os.path.split(spydermaps.__file__)[0]
if not len(spydermapsdir): spydermapsdir = "."

#load the action3 spydermap
action3spydermapfile = os.path.join(spydermapsdir, "action3spydermap.spydermap")
import spyder, Spyder
import bee  #defines the Spydermap datamodel

action3spydermap = Spyder.Spydermap.fromfile(action3spydermapfile)

from bee.spyderhive.spydermaphive import spydermapframe


class action3spydermaphive(spydermapframe):
    spydermap = action3spydermap

#import workers
from workers.action3_play_animation import action3_play_animation
from workers.action3_play_sound import action3_play_sound
#import drones
from workers.action3drones import animationmanager
from workers.action3drones import soundmanager

#define action3 hive
import bee
from bee import Antenna, connect


class action3hive(bee.frame):
    animationmanager = animationmanager()
    soundmanager = soundmanager()
    actionspydermap = action3spydermaphive(
        animationmanager=animationmanager,
        soundmanager=soundmanager,
    )

    action3_play_animation_1 = action3_play_animation()
    action3_play_sound_1 = action3_play_sound()

    animplay = Antenna(action3_play_animation_1.inp)
    soundplay = Antenna(action3_play_sound_1.inp)
