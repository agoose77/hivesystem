import bee
from bee import *
import dragonfly
from dragonfly.commandhive import commandhive
from dragonfly.sys import exitactuator
from dragonfly.io import display, commandsensor
from components.workers.chessprocessor import chessprocessor
from components.workers.chesskeeper import chesskeeper

class myhive(commandhive):  
  com = commandsensor()

  g = chessprocessor()
  k = chesskeeper()
  connect(k, g)
  connect(com, g)
  connect(g, k)
  
  d = display("str")()
  connect(g, d)

  ex = exitactuator()
  connect(g.finished, ex)

        
m = myhive().getinstance()
m.build("m")
m.place()
m.close()

m.init()

m.run()
