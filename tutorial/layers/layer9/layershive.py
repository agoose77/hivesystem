#translation of layers.hivemap to hive system Python code

#load the action hives
from action1 import action1hive
from action2 import action2hive
from action3 import action3hive

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
  action1 = action1hive()
  
  vwalk = variable("id")("walk")
  keyW = dragonfly.io.keyboardsensor_trigger("W")
  transistor_1 = transistor("id")()
  connect(vwalk, transistor_1)
  connect(keyW, transistor_1)
  connect(transistor_1, action1.animplay)
  connect(transistor_1, action1.soundplay)
  
  vjump = variable("id")("jump")
  keyTAB = dragonfly.io.keyboardsensor_trigger("TAB")
  transistor_2 = transistor("id")()
  connect(vjump, transistor_2)
  connect(keyTAB, transistor_2)
  connect(transistor_2, action1.animplay)
  connect(transistor_2, action1.soundplay)

  #action 2
  action2 = action2hive()
  
  vrun = variable("id")("run")
  keyR = dragonfly.io.keyboardsensor_trigger("R")
  transistor_4 = transistor("id")()
  connect(vrun, transistor_4)
  connect(keyR, transistor_4)
  connect(transistor_4, action2.actionplay)
  
  vshoot = variable("id")("shoot")
  keySPACE = dragonfly.io.keyboardsensor_trigger("SPACE")
  transistor_3 = transistor("id")()
  connect(vshoot, transistor_3)
  connect(keySPACE, transistor_3)
  connect(transistor_3, action2.actionplay)

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
  
