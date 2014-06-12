from bee import *
from dragonfly.sys import startsensor
from dragonfly.std import variable
from dragonfly.time.push import sleep
from .chessUCI import chessUCI

import spyder, Spyder
from .spydercomputer import ParamComputer_698767
# (698767 is just a random ID to prevent future name clashes)

class computer2b(frame):
    params = parameter("ParamComputer_698767")

    par = get_parameter("params")
    p = chessUCI(par.player, par.engine_binary, par.engine_dir)
    del par
    start = startsensor()
    connect(start, p.trigger_get_move)

    delay = variable(("float", "quantity"))(1.0)
    delayed_move = sleep("trigger")()
    connect(delay, delayed_move)
    connect(delayed_move, p.trigger_get_move)

    turn = antenna(p.turn)
    trigger_move = antenna(delayed_move.inp)
    make_move = antenna(p.make_move)
    move = output(p.get_move)
