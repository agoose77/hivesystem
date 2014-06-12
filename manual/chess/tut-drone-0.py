import bee
import dragonfly
from dragonfly.commandhive import commandhive


class myhive(commandhive):
    pass


m = myhive().getinstance()
m.build("m")
m.place()
m.close()

m.init()

m.run()

