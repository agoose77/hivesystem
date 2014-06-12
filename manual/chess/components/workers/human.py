from bee import *

from dragonfly.logic import filter
from dragonfly.op.pull import equal2


class human(frame):
    player = parameter("str")

    p = filter(("str", "chess"))()
    turn_p = equal2("str")(get_parameter("player"))
    connect(turn_p, p.filter)

    com = antenna(p.inp)
    turn = antenna(turn_p.inp)
    move = output(p.true)
