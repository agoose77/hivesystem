import bee
from bee import *
import dragonfly
from dragonfly.commandhive import commandhive
from dragonfly.io import display, commandsensor


class myhive(commandhive):
    com = commandsensor()
    d = display("str")()
    connect(com, d)


m = myhive().getinstance()
m.build("m")
m.place()
m.close()

m.init()

m.run()
