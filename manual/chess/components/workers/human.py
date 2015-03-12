from bee import *

from dragonfly.logic import filter
from dragonfly.op.pull import equal2


class human(frame):
    player = Parameter("str")

    p = filter(("str", "chess"))()
    turn_p = equal2("str")(ParameterGetter("player"))
    connect(turn_p, p.filter)

    com = Antenna(p.inp)
    turn = Antenna(turn_p.inp)
    move = Output(p.true)
