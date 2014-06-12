import bee
from bee import *
import dragonfly
from dragonfly.commandhive import commandhive, commandapp
from dragonfly.sys import exitactuator
from dragonfly.io import display, commandsensor
from dragonfly.std import variable, transistor, test
from dragonfly.sys import on_next
from components.workers.chessprocessor2 import chessprocessor2
from components.workers.chesskeeper import chesskeeper
from components.workers.chessboard2 import chessboard2
from components.workers.except_valueerror import except_valueerror

from components.workers.human import human
from components.workers.computer import computer

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

    p1 = human("Black")
    connect(com, p1.com)
    connect(turn, p1.turn)

    p2 = computer("White", "glaurung")
    connect(g.turn, p2.turn)
    connect(on_next, p2.trigger_move)

    k = chesskeeper()
    connect(k, g)
    connect(p1.move, g)
    connect(p2.move, g)
    connect(g, k)
    connect(g, p2.make_move)

    b = chessboard2("Black")
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
