import bee
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *
  
class tetris_control(bee.worker):
  blockgrid = antenna('pull', ('object', 'bgrid'))
  
  
  def get_grids(self):
      self.get_grid1()
      self.get_grid2()
                                                                                                    
  
  grid1 = buffer('pull', ('object', 'bgrid'))
  
  
  get_grid1 = triggerfunc(grid1)
  
  grid2 = buffer('pull', ('object', 'bgrid'))
  
  
  get_grid2 = triggerfunc(grid2)
  
  @modifier
  def m_place_init(self):
    self.get_grids()
    dx = int(self.grid1.maxx/2)-self.grid2.minx
    self.grid2.maxx += dx
    self.grid2.minx += dx
    dy = self.grid1.maxy - self.grid2.maxy  
    self.grid2.maxy += dy
    self.grid2.miny += dy    
                                                                                 
  
  maingrid = antenna('pull', ('object', 'bgrid'))
  
  place_init = antenna('push', 'trigger')
  
  connect(maingrid, grid1)
  connect(blockgrid, grid2)
  trigger(place_init, m_place_init)
  
