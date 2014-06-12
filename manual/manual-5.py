import dragonfly.pandahive
from dragonfly.grid import bgrid
from dragonfly.canvas import box2d
import random

import dragonfly.sys, dragonfly.io, dragonfly.std, dragonfly.gen

#create 100x100 binary grid and randomize it
grid = bgrid(minx=1,maxx=100,miny=1,maxy=100)
def randomize_grid():
  for n in range(grid.minx,grid.maxx+1):
    for nn in range(grid.miny,grid.maxy+1):
      if random.random() < 0.5: grid.set_true(n,nn)
      else: grid.set_false(n,nn)
randomize_grid()

#set up drawing parameters for the grid
class parameters(object): 
  pass
box = box2d(x=100,y=50,sizex=500,sizey=500)
params = parameters()
params.color = (0.7,0.7,0.7,0)

gridparamtype = (("object","bgrid"),("object","box2d"),"object")

#create our main hive class
from bee import connect, reference
class myhive(dragonfly.pandahive.pandahive):
  canvas = dragonfly.pandahive.pandacanvas()
  
  start = dragonfly.sys.startsensor()
  grid = dragonfly.std.variable(gridparamtype)((reference(grid),box,params))
  draw = dragonfly.canvas.draw(("object","bgrid"))()
  do_draw = dragonfly.std.transistor(gridparamtype)()
  connect(grid, do_draw)
  connect(do_draw, draw)
  connect(start, do_draw) 
  
  ticksensor = dragonfly.io.ticksensor()
  call = dragonfly.gen.call0(randomize_grid)
  connect(ticksensor, call)
  update = dragonfly.canvas.update1()
  do_update = dragonfly.std.transistor("id")()
  connect(draw, do_update)
  connect(do_update, update)
  connect(ticksensor, do_update)

#initialize our hive
m = myhive().getinstance()
m.build("myhive")
m.place()
m.close()
m.init()  

#draw the grid and run
m.run()
