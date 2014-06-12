from __future__ import print_function

# import the main and action workers
from mainworker import mainworker
from action1 import action1worker
from action2 import action2worker
from action3 import action3worker

#import drones
from action3drones import animationmanager
from action3drones import soundmanager

#define mainhive
import bee
from dragonfly.consolehive import consolehive
from bee import connect


class mainhive(consolehive):
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
# First fire a start event, then a tick event on each tick
# Drones and workers get activated by responding to these events
main.run()
