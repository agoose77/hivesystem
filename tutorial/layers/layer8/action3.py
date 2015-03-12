# translation of action3.hivemap into hive system Python code

#import configuration
from conf.action3conf import action3conf

#import workers
from actionworkers import action3_play_animation
from actionworkers import action3_play_sound
#import drones
from action3drones import animationmanager
from action3drones import soundmanager

#define action3 hive
import bee
from bee import Antenna, connect


class action3hive(bee.frame):
    animationmanager = animationmanager()
    soundmanager = soundmanager()

    actionspyderhive = action3conf(
        animationmanager=animationmanager,
        soundmanager=soundmanager,
    )

    action3_play_animation_1 = action3_play_animation()
    action3_play_sound_1 = action3_play_sound()

    animplay = Antenna(action3_play_animation_1.inp)
    soundplay = Antenna(action3_play_sound_1.inp)
