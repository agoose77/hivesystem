import bee
from bee import *
import dragonfly
from dragonfly.commandhive import commandhive, commandapp
from dragonfly.sys import exitactuator
from dragonfly.io import display, commandsensor
from dragonfly.logic import filter
from dragonfly.op.pull import equal2
from dragonfly.std import variable, transistor
from dragonfly.sys import on_next
from components.workers.chessprocessor2 import chessprocessor2
from components.workers.chesskeeper import chesskeeper
from components.workers.chessboard import chessboard
from components.workers.except_valueerror import except_valueerror

from direct.showbase.ShowBase import taskMgr

from panda3d.core import getModelPath
import os

getModelPath().prependPath(os.getcwd())

from bee import hivemodule


class myapp(commandapp):
    def on_tick(self):
        taskMgr.step()
        taskMgr.step()


class myhive(commandhive):
    _hivecontext = hivemodule.appcontext(myapp)

    g = chessprocessor2()
    exc_v = except_valueerror()
    connect(g.evexc, exc_v)

    com = commandsensor()

    turn = variable("str")("White")
    t_turn = transistor("str")()
    connect(g.turn, t_turn)
    connect(t_turn, turn)

    on_next = on_next()
    connect(on_next, t_turn)
    connect(g.made_move, on_next)

    p1 = filter(("str", "chess"))()
    connect(com, p1)
    turn_white = equal2("str")("White")
    connect(turn, turn_white)
    connect(turn_white, p1.filter)

    p2 = filter(("str", "chess"))()
    connect(com, p2)
    turn_black = equal2("str")("Black")
    connect(turn, turn_black)
    connect(turn_black, p2.filter)

    k = chesskeeper()
    connect(k, g)
    connect(p1.true, g)
    connect(p2.true, g)
    connect(g, k)

    b = chessboard()
    connect(turn, b.turn)
    connect(b.get_move, g)
    connect(g, b.make_move)

    d = display("str")()
    connect(g, d)

    ex = exitactuator()
    connect(g.finished, ex)

    raiser = bee.raiser()
    bee.connect("evexc", raiser)


m = myhive().getinstance()
m.build("m")
m.place()
m.close()

m.init()

m.run()
