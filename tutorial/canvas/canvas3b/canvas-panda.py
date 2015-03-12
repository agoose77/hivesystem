from __future__ import print_function

# Load any custom data models for this project
import spyder, Spyder
import spydermodels, spyderhives

#Load the hivemap (visual hive, edited with HiveGUI)
import bee  #defines the Hivemap datamodel

hivemap = Spyder.Hivemap.fromfile("canvas-panda.hivemap")

#Put the hivemap inside a hivemaphive, which interprets the hivemap
# We are using a frame hive, sharing the environment with its parent
from bee.spyderhive.hivemaphive import hivemapframe


class mainhivemaphive(hivemapframe):
    hivemap = hivemap

#Embed the hivemaphive inside our main hive
# As main hive, we choose the pandahive 
# The pandahive provides a Panda3D environment
from dragonfly.pandahive import pandahive


class mainhive(pandahive):
    hivemaphive = mainhivemaphive()

    raiser = bee.raiser()
    bee.connect("evexc", raiser)


#Set up the main hive and run it

# This part is constant for every main hive

#Give us a new mainhive instance
main = mainhive().getinstance()

#Build a context tree named "main", and Configure its bees
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
