import bee
from bee import *
import dragonfly
from dragonfly.commandhive import commandhive
from dragonfly.sys import exitactuator
from dragonfly.io import display, commandsensor
from dragonfly.logic import filter
from dragonfly.op.pull import equal2
from components.workers.chessprocessor import chessprocessor
from components.workers.chesskeeper import chesskeeper


class myhive(commandhive):
    g = chessprocessor()
    com = commandsensor()

    p1 = filter(("str", "chess"))()
    connect(com, p1)
    turn_white = equal2("str")("White")
    connect(g.turn, turn_white)
    connect(turn_white, p1.filter)

    p2 = filter(("str", "chess"))()
    connect(com, p2)
    turn_black = equal2("str")("Black")
    connect(g.turn, turn_black)
    connect(turn_black, p2.filter)

    k = chesskeeper()
    connect(k, g)
    connect(p1.true, g)
    connect(p2.true, g)
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
