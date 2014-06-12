import bee
import dragonfly.pandahive
from dragonfly.grid import bgrid
from dragonfly.canvas import box2d

blocks = (
  bgrid(values=((0,0),(1,0),(2,0),(3,0))), #I
  bgrid(values=((0,1),(0,0),(1,0),(2,0))), #J
  bgrid(values=((0,0),(1,0),(2,0),(2,1))), #L
  bgrid(values=((0,1),(0,0),(1,1),(1,0))), #O
  bgrid(values=((0,0),(1,0),(1,1),(2,0))), #S
  bgrid(values=((0,0),(1,0),(1,1),(2,0))), #T
  bgrid(values=((0,1),(1,1),(1,0),(2,0))), #Z
)

class main(dragonfly.pandahive.pandahive):
  blocks = blocks
  gridx = 10
  gridy = 20  
  mainarea = box2d(100,150,300,500)
  scorearea = box2d(170,100,80,40)
