from bee import *
from dragonfly.sys import startsensor
from dragonfly.std import variable
from dragonfly.time.push import sleep
from .chessUCI import chessUCI

from .computer import computer


class computer2a(computer):
    delay = variable(("float", "quantity"))(1.0)
    delayed_move = sleep("trigger")()
    connect(delay, delayed_move)
    connect(delayed_move, ("p", "trigger_get_move"))

    trigger_move = Antenna(delayed_move.inp)
