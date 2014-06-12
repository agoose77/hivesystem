import bee
import dragonfly
from dragonfly.commandhive import commandhive

from dragonfly.sys import startsensor, on_next, exitactuator

class myhive(commandhive):
  s = startsensor()
  o = on_next()
  e = exitactuator()
  bee.connect(s,o)
  bee.connect(o,e)
        
m = myhive().getinstance()
m.build("m")
m.place()
m.close()

m.init()

m.run()
