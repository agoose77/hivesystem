from __future__ import print_function

# import the "layers" hive
from layershive import layershive

#Embed the "layers" hive inside our main hive
# As main hive, we choose the console hive 
# The console hive provides a console environment for key presses
import bee
from dragonfly.consolehive import consolehive


class mainhive(consolehive):
    layershive = layershive()

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
