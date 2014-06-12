import bee
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *
  
import copy
            


class tetris_control(bee.worker):
  blockgrid = antenna('pull', ('object', 'bgrid'))
  
  dropped = output('push', 'trigger')
  trig_dropped = triggerfunc(dropped)
  
  
  
  def get_grids(self):
      self.get_grid1()
      self.get_grid2()
                                                                                                    
  
  grid1 = buffer('pull', ('object', 'bgrid'))
  
  
  get_grid1 = triggerfunc(grid1)
  
  grid2 = buffer('pull', ('object', 'bgrid'))
  
  
  get_grid2 = triggerfunc(grid2)
  
  lost = output('push', 'trigger')
  trig_lost = triggerfunc(lost)
  
  
  @modifier
  def m_move_down(self):
    self.get_grids()
    block = copy.copy(self.grid2)
    block.translate(0,-1)
    if block.miny < 0 or self.grid1.overlap(block):
      self.grid1.merge(self.grid2)
      self.trig_dropped()
    else:
      self.grid2.translate(0,-1)                                                                                                     
  
  @modifier
  def m_place_init(self):
    self.get_grids()
    dx = int(self.grid1.maxx/2)-self.grid2.minx
    self.grid2.maxx += dx
    self.grid2.minx += dx
    dy = self.grid1.maxy - self.grid2.maxy  
    self.grid2.maxy += dy
    self.grid2.miny += dy    
    if self.grid1.overlap(self.grid2): 
       self.trig_lost()                                                                                
  
  maingrid = antenna('pull', ('object', 'bgrid'))
  
  move_down = antenna('push', 'trigger')
  
  place_init = antenna('push', 'trigger')
  
  connect(maingrid, grid1)
  connect(blockgrid, grid2)
  trigger(place_init, m_place_init)
  trigger(move_down, m_move_down)
  
