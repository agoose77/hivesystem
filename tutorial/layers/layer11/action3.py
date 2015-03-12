# import workers
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

    init_animationmanager = bee.init(animationmanager)
    init_soundmanager = bee.init(soundmanager)

    init_animationmanager.add_animation("swim", "splash-animation")
    init_soundmanager.add_sound("swim", "splash.wav")

    init_animationmanager.add_animation("crouch", "crouching")
    init_soundmanager.add_sound("crouch", "crouch.wav")

    action3_play_animation_1 = action3_play_animation()
    action3_play_sound_1 = action3_play_sound()

    animplay = Antenna(action3_play_animation_1.inp)
    soundplay = Antenna(action3_play_sound_1.inp)
