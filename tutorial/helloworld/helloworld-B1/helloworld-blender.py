###
#Import the workers that we are going to use 
import bee
from bee import connect
import dragonfly.std
import dragonfly.io
###

# As main hive, we choose the blenderhive 
# The blenderhive provides a Blender Game Engine (BGE) environment
from dragonfly.blenderhive import blenderhive
class mainhive(blenderhive):
  
  ###
  #Create and connect the workers
  variable_str_1 = dragonfly.std.variable_str("Hello world!")
  sync_1 = dragonfly.std.sync("str")()
  display_str_1 = dragonfly.io.display_str()
  connect(variable_str_1, sync_1)
  connect(sync_1, display_str_1)
  ###
  
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
