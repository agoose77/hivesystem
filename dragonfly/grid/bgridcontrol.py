import bee
from bee.segments import *
import copy

class bgridcontrol(bee.worker):
  grid = antenna("pull",("object","bgrid"))
  v_grid = buffer("pull",("object","bgrid"))
  get_grid = triggerfunc(v_grid, "input")
  connect(grid, v_grid)

  set = antenna("push",("object","bgrid"))
  v_set = variable(("object","bgrid"))
  connect(set, v_set)
  @modifier
  def m_set(self):
    self.get_grid()
    self.v_grid.set(self.v_set)
  trigger(v_set, m_set)
  
  set_true = antenna("push",("int","int"))
  v_set_true = variable(("int","int"))
  connect(set_true, v_set_true)
  @modifier
  def m_set_true(self):
    self.get_grid()
    x,y = self.v_set_true
    self.v_grid.set_true(x,y)
  trigger(v_set_true, m_set_true)    

  set_false = antenna("push",("int","int"))
  v_set_false = variable(("int","int"))
  connect(set_false, v_set_false)
  @modifier
  def m_set_false(self):
    self.get_grid()
    x,y = self.v_set_false
    self.v_grid.set_false(x,y)
  trigger(v_set_false, m_set_false)

  copy = output("pull",("object","bgrid"))
  v_copy = variable(("object","bgrid"))
  connect(v_copy, copy)
  @modifier
  def m_copy(self):
    self.get_grid()
    self.v_copy = copy.deepcopy(self.v_grid)
  pretrigger(v_copy,m_copy)
  
  get_value = output("pull","bool")
  v_get_value = variable("bool")
  get_value_pos = antenna("pull",("int","int"))
  b_get_value_pos = buffer("pull",("int","int"))
  connect(get_value_pos, b_get_value_pos)
  trig_get_value_pos = triggerfunc(b_get_value_pos,"update")
  connect(v_get_value, get_value)
  @modifier
  def m_get_value(self):
    self.trig_get_value_pos()
    x,y = self.b_get_value_pos
    self.get_grid()
    self.v_get_value = self.v_grid.get_value(x,y)
  pretrigger(v_get_value, m_get_value)

  merge = antenna("push",("object","bgrid"))
  v_merge = variable(("object","bgrid"))
  connect(merge, v_merge)
  @modifier
  def m_merge(self):
    self.get_grid()
    self.v_grid.merge(self.v_merge)
  trigger(v_merge, m_merge, "update")

  overlap = output("pull","bool")
  v_overlap = variable("bool")
  connect(v_overlap, overlap)
  overlap_grid = antenna("pull", ("object","bgrid"))
  v_overlap_grid = buffer("pull", ("object","bgrid"))
  connect(overlap_grid, v_overlap_grid)
  get_overlap_grid = triggerfunc(v_overlap_grid,"update")
  @modifier
  def m_overlap(self):
    self.get_overlap_grid()
    self.get_grid()
    overlap = self.v_grid.overlap(self.v_overlap_grid)
    self.v_overlap = overlap
  pretrigger(v_overlap, m_overlap)
  
  rotate = antenna("push","int")
  v_rotate = variable("int")
  connect(rotate,v_rotate)
  @modifier 
  def m_rotate(self):
    self.get_grid()
    self.v_grid.rotate(self.v_rotate)
  trigger(v_rotate, m_rotate)
  
  translate = antenna("push",("int","int"))
  v_translate = variable(("int", "int"))
  connect(translate, v_translate)
  @modifier
  def m_translate(self):
    self.get_grid()
    self.v_grid.translate(*self.v_translate)
  trigger(v_translate, m_translate)
    
  
  
