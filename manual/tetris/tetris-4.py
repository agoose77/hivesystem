import copy
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

from bee.segments import *


class tetris_init_main(bee.worker):
    gridx = variable("int")
    parameter(gridx)
    gridy = variable("int")
    parameter(gridy)

    start = antenna("push", "trigger")
    outp = output("push", ("object", "bgrid"))
    grid = variable(("object", "bgrid"))
    t_outp = transistor(("object", "bgrid"))
    connect(grid, t_outp)
    connect(t_outp, outp)
    trig = triggerfunc(t_outp)

    @modifier
    def m_start(self):
        self.grid = bgrid(0, self.gridx - 1, 0, self.gridy - 1)
        self.trig()

    trigger(start, m_start)


class tetris_control(bee.worker):
    maingrid = antenna("pull", ("object", "bgrid"))
    blockgrid = antenna("pull", ("object", "bgrid"))
    grid1 = buffer("pull", ("object", "bgrid"))
    connect(maingrid, grid1)
    grid2 = buffer("pull", ("object", "bgrid"))
    connect(blockgrid, grid2)
    get_grids = triggerfunc(grid1, "input")
    trigger(grid1, grid2, "input", "input")

    lost = output("push", "trigger")
    trig_lost = triggerfunc(lost)

    place_init = antenna("push", "trigger")

    @modifier
    def m_place_init(self):
        self.get_grids()
        dx = int(self.grid1.maxx / 2) - self.grid2.minx
        self.grid2.maxx += dx
        self.grid2.minx += dx
        dy = self.grid1.maxy - self.grid2.maxy
        self.grid2.maxy += dy
        self.grid2.miny += dy
        if self.grid1.overlap(self.grid2):
            self.trig_lost()

    trigger(place_init, m_place_init)


from bee import antenna, output, connect, attribute, configure, parameter, get_parameter


class tetris_select_block(bee.frame):
    blocks = parameter("object")
    blocks_ = get_parameter("blocks")
    w_blocks = dragonfly.gen.gentuple2(blocks_)
    sel = dragonfly.random.choice()
    connect(w_blocks, sel)

    do_select = dragonfly.gen.transistor()
    connect(sel, do_select)

    chosen = dragonfly.std.variable(("object", "bgrid"))(emptygrid)
    chosencontrol = dragonfly.grid.bgridcontrol()
    connect(chosen, chosencontrol.grid)
    connect(do_select, chosen)
    do_select2 = dragonfly.gen.transistor()
    connect(chosen, do_select2)

    uptofour = dragonfly.std.variable(("int", "int"))((0, 4))
    randint = dragonfly.random.randint()
    connect(uptofour, randint)
    rotate = dragonfly.std.transistor("int")()
    connect(randint, rotate)
    connect(rotate, chosencontrol.rotate)

    trigger = dragonfly.std.pushconnector("trigger")()
    connect(trigger, do_select)
    connect(trigger, rotate)
    connect(trigger, do_select2)

    select = antenna(trigger.inp)
    selected = output(do_select2.outp)


class tetris_draw(bee.frame):
    mainarea_ = attribute("parent", "mainarea")
    mainarea_id_ = attribute("parent", "mainarea_id")

    drawgrid = dragonfly.std.variable(("object", "bgrid"))(emptygrid)
    drawgridcontrol = dragonfly.grid.bgridcontrol()
    connect(drawgrid, drawgridcontrol.grid)
    w_draw = dragonfly.canvas.draw3(("object", "bgrid"))(mainarea_id_)
    do_draw = dragonfly.std.transistor(("object", "bgrid"))()
    connect(drawgrid, do_draw)
    connect(do_draw, w_draw)
    update = dragonfly.canvas.update3(mainarea_id_)

    maingridcontrol = dragonfly.grid.bgridcontrol()
    copy_maingrid = dragonfly.std.transistor(("object", "bgrid"))()
    connect(maingridcontrol.copy, copy_maingrid)
    connect(copy_maingrid, drawgridcontrol.set)
    t_blockgrid = dragonfly.std.transistor(("object", "bgrid"))()
    connect(t_blockgrid, drawgridcontrol.merge)

    trigger = dragonfly.std.pushconnector("trigger")()
    connect(trigger, copy_maingrid)
    connect(trigger, t_blockgrid)
    connect(trigger, update)

    start = antenna(do_draw.trig)
    maingrid = antenna(maingridcontrol.grid)
    blockgrid = antenna(t_blockgrid.inp)
    draw = antenna(trigger.inp)


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

    canvas = dragonfly.pandahive.pandacanvas()

    blocks_ = attribute("blocks")
    gridx_ = attribute("gridx")
    gridy_ = attribute("gridy")
    mainarea_ = attribute("mainarea")
    mainarea_parameters_ = attribute("mainarea_parameters")
    mainarea_id_ = attribute("mainarea_id")
    scorearea_ = attribute("scorearea")
    scorearea_id_ = attribute("scorearea_id")

    c0 = configure("canvas")  # must have a lower-alphabet name than "canvas"
    c0.reserve(mainarea_id_, ("object", "bgrid"), box=mainarea_, parameters=mainarea_parameters_)

    maingrid = dragonfly.std.variable(("object", "bgrid"))(emptygrid)
    maingridcontrol = dragonfly.grid.bgridcontrol()
    connect(maingrid, maingridcontrol.grid)

    blockgrid = dragonfly.std.variable(("object", "bgrid"))(emptygrid)
    blockgridcontrol = dragonfly.grid.bgridcontrol()
    connect(blockgrid, blockgridcontrol.grid)

    select_block = tetris_select_block(blocks=blocks_)
    connect(select_block, blockgridcontrol.set)
    init_main = tetris_init_main(gridx_, gridy_)
    connect(init_main, maingridcontrol.set)
    draw = tetris_draw()
    connect(maingrid, draw.maingrid)
    connect(blockgrid, draw.blockgrid)

    control = tetris_control()
    connect(maingrid, control.maingrid)
    connect(blockgrid, control.blockgrid)

    start = dragonfly.sys.startsensor()
    connect(start, select_block)
    connect(start, init_main.start)
    connect(start, control.place_init)
    connect(start, draw.start)
    connect(start, draw.draw)

    raiser = bee.raiser()
    connect("evexc", raiser)


m = main().getinstance()
m.build("main")
m.place()
m.close()
m.init()
m.run()
