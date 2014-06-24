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

from bee import antenna, output, connect, attribute, parameter, get_parameter


class tetris_select_block(bee.frame):
    blocks = parameter("object")
    blocks_ = get_parameter("blocks")
    w_blocks = dragonfly.gen.gentuple2(blocks_)
    sel = dragonfly.random.choice()
    connect(w_blocks, sel)

    do_select = dragonfly.gen.transistor()
    connect(sel, do_select)

    select = antenna(do_select.trig)
    selected = output(do_select.outp)


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

    select_block = tetris_select_block(blocks=blocks_)

    test = dragonfly.std.trigger()
    connect(test, select_block)
    connect(select_block, blockgrid)


m = main().getinstance()
m.build("main")
m.place()
m.close()
m.init()
print
"BLOCKS:"
for g in m.select_block.w_blocks.set_property_value(): print
g.get_values()
print
"SELECTED :", m.blockgrid.value.get_values()
m.test.trigger()
print
"SELECTED :", m.blockgrid.value.get_values()


class main2(main):
    blocks = blocks[:3]


m2 = main2().getinstance()
m2.build("main2")
m2.place()
m2.close()
m2.init()
print
"BLOCKS2:"
for g in m2.select_block.w_blocks.set_property_value(): print
g.get_values()
print
"SELECTED2:", m2.blockgrid.value.get_values()
m2.test.trigger()
print
"SELECTED2:", m2.blockgrid.value.get_values()
print
"SELECTED :", m.blockgrid.value.get_values()
    
