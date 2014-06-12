from __future__ import print_function

# import the main and action workers
from mainworker import mainworker
from action1 import action1worker
from action2 import action2worker
from action3 import action3worker

#import drones
from action3drones import animationmanager
from action3drones import soundmanager

#keyboard mainloop
from keycodes import ascii_to_keycode
from getch import getch, kbhit, change_termios, restore_termios


def mainloop(keyfunc=None):
    change_termios()
    while True:
        while not kbhit(): continue
        key = getch()
        if isinstance(key, bytes) and bytes != str: key = key.decode()
        if key not in ascii_to_keycode: continue
        keycode = ascii_to_keycode[key]
        if keycode == "ESCAPE": break
        if keyfunc is not None: keyfunc(keycode)
    restore_termios()

#define mainhive
import bee
from bee import inithive
from bee import connect


class mainhive(inithive):
    #action3 manager drones
    animationmanager = animationmanager()
    soundmanager = soundmanager()

    #main worker and action workers
    mainworker = mainworker()
    action1 = action1worker()
    connect(mainworker.action1_anim, action1.animplay)
    connect(mainworker.action1_sound, action1.soundplay)
    action2 = action2worker()
    connect(mainworker.action2, action2.actionplay)
    action3 = action3worker()
    connect(mainworker.action3_anim, action3.animplay)
    connect(mainworker.action3_sound, action3.soundplay)

    #exception handling
    raiser = bee.raiser()
    bee.connect("evexc", raiser)


#Set up the main hive and run it

# This part is constant for every main hive

#Give us a new mainhive instance
main = mainhive().getinstance()

#Build a context tree named "main", and configure its bees
main.build("main")

#Declare sockets and plugins
main.place()

#Build all connections, and validate the connection network
main.close()

#Set start values and other initialization routines
main.init()

#Run the main loop
main.mainworker.start()
mainloop(main.mainworker.keypress)
