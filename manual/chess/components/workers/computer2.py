from bee import *
from dragonfly.sys import startsensor
from dragonfly.std import variable
from dragonfly.time.push import sleep
from .chessUCI import chessUCI


class computer2(frame):
    par1_player = Parameter("str")
    par2_engine_binary = Parameter("str")
    par3_engine_dir = Parameter("str", None)

    p = chessUCI(ParameterGetter("par1_player"), ParameterGetter("par2_engine_binary"), ParameterGetter("par3_engine_dir"))
    start = startsensor()
    connect(start, p.trigger_get_move)

    delay = variable(("float", "quantity"))(1.0)
    delayed_move = sleep("trigger")()
    connect(delay, delayed_move)
    connect(delayed_move, p.trigger_get_move)

    turn = Antenna(p.turn)
    trigger_move = Antenna(delayed_move.inp)
    make_move = Antenna(p.make_move)
    move = Output(p.get_move)
