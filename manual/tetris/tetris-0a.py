import bee
import dragonfly.pandahive
from dragonfly.grid import bgrid
from dragonfly.canvas import box2d

import dragonfly.std, dragonfly.gen, dragonfly.random

blocks = (
    bgrid(values=((0, 0), (1, 0), (2, 0), (3, 0))),  # I
    bgrid(values=((0, 1), (0, 0), (1, 0), (2, 0))),  #J
    bgrid(values=((0, 0), (1, 0), (2, 0), (2, 1))),  #L
    bgrid(values=((0, 1), (0, 0), (1, 1), (1, 0))),  #O
    bgrid(values=((0, 0), (1, 0), (1, 1), (2, 1))),  #S
    bgrid(values=((0, 0), (1, 0), (1, 1), (2, 0))),  #T
    bgrid(values=((0, 1), (1, 1), (1, 0), (2, 0))),  # Z
)

emptygrid = bgrid(0, 0, 0, 0)

from bee import connect, attribute


class parameters(object):
    def __init__(self, **args):
        for a in args: setattr(self, a, args[a])


class main(dragonfly.pandahive.pandahive):
    blocks = blocks
    gridx = 10
    gridy = 20
    mainarea = box2d(100, 150, 225, 375)
    mainarea_id = "main"
    mainarea_parameters = parameters(color=(0.5, 0.5, 0.5, 0))
    scorearea = box2d(170, 100, 80, 40)
    scorearea_id = "score"

    # define bee.attribute derivatives, allowing proper inheritance
    blocks_ = attribute("blocks")
    gridx_ = attribute("gridx")
    gridy_ = attribute("gridy")
    mainarea_ = attribute("mainarea")
    mainarea_parameters_ = attribute("mainarea_parameters")
    mainarea_id_ = attribute("mainarea_id")
    scorearea_ = attribute("scorearea")
    scorearea_id_ = attribute("scorearea_id")

    maingrid = dragonfly.std.variable(("object", "bgrid"))(emptygrid)
    maingridcontrol = dragonfly.grid.bgridcontrol()
    connect(maingrid, maingridcontrol.grid)

    blockgrid = dragonfly.std.variable(("object", "bgrid"))(emptygrid)
    blockgridcontrol = dragonfly.grid.bgridcontrol()
    connect(blockgrid, blockgridcontrol.grid)
    
