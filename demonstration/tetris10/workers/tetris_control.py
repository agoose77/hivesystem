import bee
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *
  
import copy
            


class tetris_control(bee.worker):
  blockgrid = antenna('pull', ('object', 'bgrid'))
  
  drop = antenna('push', 'trigger')
  
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
  def m_drop(self):
    self.get_grids()
    block = copy.copy(self.grid2)
    while block.miny >= 0 and not self.grid1.overlap(block):
      block.translate(0,-1)
    block.translate(0,1)
    self.grid1.merge(block)
    self.trig_dropped()                                                                                               
  
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
  def m_move_left(self):
    self.move_sideways(-1) 
  
  @modifier
  def m_move_right(self):
    self.move_sideways(1)   
  
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
  
  @modifier
  def m_rotate_ccw(self):
    self.rotate(1)    
  
  @modifier
  def m_rotate_cw(self):
    self.rotate(3) 
  
  maingrid = antenna('pull', ('object', 'bgrid'))
  
  move_down = antenna('push', 'trigger')
  
  move_left = antenna('push', 'trigger')
  
  move_right = antenna('push', 'trigger')
  
  
  def move_sideways(self, direction):
    self.get_grids()
    block = copy.copy(self.grid2)
    block.translate(direction,0)
    if block.minx < 0: return
    if block.maxx > self.grid1.maxx: return
    if self.grid1.overlap(block): return
    self.grid2.translate(direction,0)                                 
  
  place_init = antenna('push', 'trigger')
  
  
  def rotate(self, times):
    self.get_grids()
    block = copy.copy(self.grid2)
    block.rotate(times)
    if block.minx < 0: 
      block.translate(-block.minx,0)
    if block.maxx > self.grid1.maxx: 
      block.translate(self.grid1.maxx-block.maxx,0)
    if self.grid1.overlap(block): return
    self.grid2.set(block)                                         
  
  rotate_ccw = antenna('push', 'trigger')
  
  rotate_cw = antenna('push', 'trigger')
  
  connect(maingrid, grid1)
  connect(blockgrid, grid2)
  trigger(place_init, m_place_init)
  trigger(move_down, m_move_down)
  trigger(move_left, m_move_left)
  trigger(move_right, m_move_right)
  trigger(drop, m_drop)
  trigger(rotate_cw, m_rotate_cw)
  trigger(rotate_ccw, m_rotate_ccw)
  
