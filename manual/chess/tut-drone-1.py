import bee
import dragonfly
from dragonfly.commandhive import commandhive

from components.drones.keyboardmove import keyboardmove
from components.drones.chessprocessor import chessprocessor
from components.drones.chesskeeper import chesskeeper
from components.drones.movereporter import movereporter


class myhive(commandhive):
    keyboardmove("White")
    keyboardmove("Black")
    chessprocessor()
    chesskeeper()
    movereporter()


m = myhive().getinstance()
m.build("m")
m.place()
m.close()

m.init()

m.run()

