from bee import *
from dragonfly.sys import startsensor
from dragonfly.std import variable
from dragonfly.time.push import sleep
from .chessUCI import chessUCI


class computer2(frame):
    par1_player = parameter("str")
    par2_engine_binary = parameter("str")
    par3_engine_dir = parameter("str", None)

    p = chessUCI(get_parameter("par1_player"), get_parameter("par2_engine_binary"), get_parameter("par3_engine_dir"))
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
