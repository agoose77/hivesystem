#translation of layers.hivemap to hive system Python code

#find out where the hivemaps are
import os
import hivemaps
hivemapsdir = os.path.split(hivemaps.__file__)[0]
if not len(hivemapsdir): hivemapsdir = "."
action1hivemapfile = os.path.join(hivemapsdir, "action1.hivemap")
action2hivemapfile = os.path.join(hivemapsdir, "action2.hivemap")

#load the hivemaps
import spyder, Spyder
action1hivemap = Spyder.Hivemap.fromfile(action1hivemapfile)
action2hivemap = Spyder.Hivemap.fromfile(action2hivemapfile)

from bee.spyderhive.hivemaphive import hivemapframe
class action1hivemaphive(hivemapframe):
  hivemap = action1hivemap

class action2hivemaphive(hivemapframe):
  hivemap = action2hivemap

"""
We could also put both hivemaps into a single hivemaphive:

class actionshivemaphive(hivemapframe):
  act1 = action1hivemap
  act2 = action2hivemap

In that case, we should replace in the hive below:
   action1 = action1hivemaphive()
   action2 = action2hivemaphive()
 => actions = actionshivemaphive
and:
   (action1,"hivemap","soundplay")
 => (actions,"act1","soundplay")
 
  (action2,"hivemap","actionplay")
 => (actions,"act2","actionplay") 

"""
###

#load the action3 hive
from workers.action3 import action3hive

#define the "layers" hive
import bee
from dragonfly.std import *
import dragonfly.io
import dragonfly.sys
from bee import connect
class layershive(bee.frame):

  #START message
  variable_str_1 = variable("str")("START")
  #or: 
  # variable_str_1 = variable_str("START")
  transistor_5 = transistor("str")()
  connect(variable_str_1, transistor_5)
  startsensor_1 = dragonfly.sys.startsensor()
  connect(startsensor_1, transistor_5)
  #or:
  # connect(startsensor_1.outp, transistor_5.trig)
  display_1 = dragonfly.io.display("str")()
  connect(transistor_5, display_1)
  #or:
  # connect(transistor_5.outp, display_1.inp)
  
  #action 1
  action1 = action1hivemaphive()
  
  vwalk = variable("id")("walk")
  keyW = dragonfly.io.keyboardsensor_trigger("W")
  transistor_1 = transistor("id")()
  connect(vwalk, transistor_1)
  connect(keyW, transistor_1)
  connect(transistor_1, (action1,"hivemap","animplay"))
  connect(transistor_1, (action1,"hivemap","soundplay"))
  
  vjump = variable("id")("jump")
  keyTAB = dragonfly.io.keyboardsensor_trigger("TAB")
  transistor_2 = transistor("id")()
  connect(vjump, transistor_2)
  connect(keyTAB, transistor_2)
  connect(transistor_2, (action1,"hivemap","animplay"))
  connect(transistor_2, (action1,"hivemap","soundplay"))

  #action 2
  action2 = action2hivemaphive()
  
  vrun = variable("id")("run")
  keyR = dragonfly.io.keyboardsensor_trigger("R")
  transistor_4 = transistor("id")()
  connect(vrun, transistor_4)
  connect(keyR, transistor_4)
  connect(transistor_4, (action2,"hivemap","actionplay"))
  
  vshoot = variable("id")("shoot")
  keySPACE = dragonfly.io.keyboardsensor_trigger("SPACE")
  transistor_3 = transistor("id")()
  connect(vshoot, transistor_3)
  connect(keySPACE, transistor_3)
  connect(transistor_3, (action2,"hivemap","actionplay"))

  #action 3
  action3 = action3hive()

  vswim = variable("id")("swim")
  keyS = dragonfly.io.keyboardsensor_trigger("S")
  transistor_6 = transistor("id")()
  connect(vswim, transistor_6)
  connect(keyS, transistor_6)
  connect(transistor_6, action3.animplay)
  connect(transistor_6, action3.soundplay)

  vcrouch = variable("id")("crouch")
  keyC = dragonfly.io.keyboardsensor_trigger("C")
  transistor_7 = transistor("id")()
  connect(vcrouch, transistor_7)
  connect(keyC, transistor_7)
  connect(transistor_7, action3.animplay)
  connect(transistor_7, action3.soundplay)
  
