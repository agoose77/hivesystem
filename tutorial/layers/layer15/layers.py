from __future__ import print_function

# import the main and action drones
from maindrone import maindrone
from action1 import action1drone
from action2 import action2drone
from action3 import action3drone

#import manager drones
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
from bee import hive


class mainhive(hive):
    #action3 manager drones
    animationmanager = animationmanager()
    soundmanager = soundmanager()

    #main drone and action drones
    maindrone = maindrone()
    action1 = action1drone()
    action2 = action2drone()
    action3 = action3drone()

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

#Run the main loop
main.maindrone.start()
mainloop(main.maindrone.keypress)
