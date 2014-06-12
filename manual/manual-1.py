import dragonfly.pandahive
from dragonfly.grid import bgrid
from dragonfly.canvas import box2d
import random

#create 100x100 binary grid and randomize it
grid = bgrid(minx=1,maxx=100,miny=1,maxy=100)
for n in range(grid.minx,grid.maxx+1):
  for nn in range(grid.miny,grid.maxy+1):
    if random.random() < 0.5: grid.set_true(n,nn)

#create our main hive class
class myhive(dragonfly.pandahive.pandahive):
  canvas = dragonfly.pandahive.pandacanvas()

#initialize our hive
m = myhive().getinstance()
m.build("myhive")
m.place()
m.close()
m.init()  

#set up drawing parameters for the grid
class parameters(object): 
  pass
box = box2d(x=100,y=50,sizex=500,sizey=500)
params = parameters()
params.color = (0.7,0.7,0.7,0)

#draw the grid and run
m.canvas._draw1(("object", "bgrid"), grid,box,params)
m.run()
