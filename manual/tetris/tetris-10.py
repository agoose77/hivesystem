import copy
import bee
import dragonfly.pandahive
from dragonfly.grid import bgrid
from dragonfly.canvas import box2d

import dragonfly.std, dragonfly.gen, dragonfly.random, dragonfly.logic
import dragonfly.mutable, dragonfly.convert.pull

blocks = (
  bgrid(values=((0,0),(1,0),(2,0),(3,0))), #I
  bgrid(values=((0,1),(0,0),(1,0),(2,0))), #J
  bgrid(values=((0,0),(1,0),(2,0),(2,1))), #L
  bgrid(values=((0,1),(0,0),(1,1),(1,0))), #O
  bgrid(values=((0,0),(1,0),(1,1),(2,1))), #S
  bgrid(values=((0,0),(1,0),(1,1),(2,0))), #T
  bgrid(values=((0,1),(1,1),(1,0),(2,0))), #Z
)

emptygrid = bgrid(0,0,0,0)

from bee.segments import *

class tetris_init_main(bee.worker):
  gridx = variable("int")
  parameter(gridx)
  gridy = variable("int")
  parameter(gridy)

  start = antenna("push", "trigger")
  outp = output("push",("object","bgrid"))
  grid = variable(("object","bgrid"))
  t_outp = transistor(("object","bgrid"))
  connect(grid, t_outp)
  connect(t_outp, outp)
  trig = triggerfunc(t_outp)
  @modifier
  def m_start(self):
    self.grid = bgrid(0,self.gridx-1,0,self.gridy-1)
    self.trig()
  trigger(start, m_start)

class tetris_control(bee.worker):
  maingrid = antenna("pull",("object","bgrid")) 
  blockgrid = antenna("pull",("object","bgrid")) 
  grid1 = buffer("pull",("object","bgrid"))
  connect(maingrid, grid1)
  grid2 = buffer("pull",("object","bgrid"))
  connect(blockgrid, grid2)
  get_grids = triggerfunc(grid1, "input")
  trigger(grid1, grid2, "input","input")
  
  lost = output("push", "trigger")
  trig_lost = triggerfunc(lost)
  
  place_init = antenna("push","trigger")
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
  trigger(place_init, m_place_init)
  
  dropped = output("push","trigger")
  trig_dropped = triggerfunc(dropped)
  
  move_down = antenna("push","trigger")
  @modifier
  def m_move_down(self):
    self.get_grids()
    block = copy.copy(self.grid2)
    block.translate(0,-1)
    if block.miny < 0 or self.grid1.overlap(block):
      self.grid1.merge(self.grid2)
      self.get_score_and_rewards()
      linereward = self.remove_lines()
      self.b_newscore = self.b_score + self.b_reward_block + linereward
      self.trig_newscore()
      self.trig_dropped()
    else:
      self.grid2.translate(0,-1)
  trigger(move_down, m_move_down)

  def move_sideways(self, direction):
    self.get_grids()
    block = copy.copy(self.grid2)
    block.translate(direction,0)
    if block.minx < 0: return
    if block.maxx > self.grid1.maxx: return
    if self.grid1.overlap(block): return
    self.grid2.translate(direction,0)
    
  move_left = antenna("push","trigger")
  @modifier
  def m_move_left(self):
    self.move_sideways(-1)
  trigger(move_left, m_move_left)
  
  move_right = antenna("push","trigger")
  @modifier
  def m_move_right(self):
    self.move_sideways(1)
  trigger(move_right, m_move_right)
  
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
  
  rotate_cw = antenna("push","trigger")
  @modifier
  def m_rotate_cw(self):
    self.rotate(3)
  trigger(rotate_cw, m_rotate_cw)
  
  rotate_ccw = antenna("push","trigger")
  @modifier
  def m_rotate_ccw(self):
    self.rotate(1)
  trigger(rotate_ccw, m_rotate_ccw)
    
  drop = antenna("push","trigger")
  @modifier
  def m_drop(self):
    self.get_grids()
    block = copy.copy(self.grid2)
    while block.miny >= 0 and not self.grid1.overlap(block):
      block.translate(0,-1)
    block.translate(0,1)
    self.grid1.merge(block)
    self.get_score_and_rewards()
    linereward = self.remove_lines()
    self.b_newscore = self.b_score + self.b_reward_block + linereward
    self.trig_newscore()
    self.trig_dropped()      
  trigger(drop, m_drop)
  
  def remove_lines(self):
    values = self.grid1.get_values()
    removed = 0
    y = 0
    while y < self.grid1.maxy+1:
      line = [v for v in values if v[1] == y]
      if len(line) == self.grid1.maxx+1:
        values = [v for v in values if v[1] != y]
        values = [(v[0],v[1]-1) if v[1] > y else v for v in values]
        removed += 1
      else:
        y += 1
    if removed: 
      self.grid1.set_values(values)
      if removed == 1: return self.b_reward_line
      if removed == 2: return self.b_reward_line2
      if removed == 3: return self.b_reward_line3
      if removed == 4: return self.b_reward_line4
    return 0
  
  score = antenna("pull","int")  
  b_score = buffer("pull","int")
  connect(score, b_score)
  newscore = output("push","int") 
  b_newscore = buffer("push","int")
  connect(b_newscore, newscore)
  trig_newscore = triggerfunc(b_newscore)
  
  reward_block = antenna("pull","int")
  b_reward_block = buffer("pull","int")
  connect(reward_block, b_reward_block)
  reward_line = antenna("pull","int")
  b_reward_line = buffer("pull","int")
  connect(reward_line, b_reward_line)
  reward_line2 = antenna("pull","int")
  b_reward_line2 = buffer("pull","int")
  connect(reward_line2, b_reward_line2)
  reward_line3 = antenna("pull","int")
  b_reward_line3 = buffer("pull","int")
  connect(reward_line3, b_reward_line3)
  reward_line4 = antenna("pull","int")
  b_reward_line4 = buffer("pull","int")
  connect(reward_line4, b_reward_line4)
  
  get_score_and_rewards = triggerfunc(b_score, "update")
  trigger(b_score, b_reward_block, "update", "update")
  trigger(b_score, b_reward_line, "update", "update")
  trigger(b_score, b_reward_line2, "update", "update")
  trigger(b_score, b_reward_line3, "update", "update")
  trigger(b_score, b_reward_line4, "update", "update")   
  
from bee import antenna, output, connect, attribute, configure, parameter, get_parameter
class tetris_select_block(bee.frame): 
  blocks = parameter("object")
  blocks_ = get_parameter("blocks")
  w_blocks = dragonfly.gen.gentuple2(blocks_)
  sel = dragonfly.random.choice()
  connect(w_blocks, sel)
  
  do_select = dragonfly.gen.transistor()
  connect(sel, do_select)
  
  chosen = dragonfly.std.variable(("object","bgrid"))(emptygrid)
  chosencontrol = dragonfly.grid.bgridcontrol()
  connect(chosen, chosencontrol.grid)
  connect(do_select, chosen)
  do_select2 = dragonfly.gen.transistor()  
  connect(chosen, do_select2)
 
  uptofour = dragonfly.std.variable(("int","int"))((0,4))
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
  mainarea_ = attribute("parent","mainarea")
  mainarea_id_ = attribute("parent","mainarea_id")
    
  drawgrid = dragonfly.std.variable(("object","bgrid"))(emptygrid)
  drawgridcontrol = dragonfly.grid.bgridcontrol()
  connect(drawgrid, drawgridcontrol.grid)  
  w_draw = dragonfly.canvas.draw3(("object","bgrid"))(mainarea_id_)
  do_draw = dragonfly.std.transistor(("object","bgrid"))()
  connect(drawgrid, do_draw)
  connect(do_draw, w_draw)
  update = dragonfly.canvas.update3(mainarea_id_)  
  
  maingridcontrol = dragonfly.grid.bgridcontrol()
  copy_maingrid = dragonfly.std.transistor(("object","bgrid"))()
  connect(maingridcontrol.copy, copy_maingrid)
  connect(copy_maingrid, drawgridcontrol.set)
  t_blockgrid = dragonfly.std.transistor(("object","bgrid"))()
  connect(t_blockgrid, drawgridcontrol.merge)
  
  trigger = dragonfly.std.pushconnector("trigger")()
  connect(trigger, copy_maingrid)
  connect(trigger, t_blockgrid)
  connect(trigger, update)

  start = antenna(do_draw.trig)
  maingrid = antenna(maingridcontrol.grid)
  blockgrid = antenna(t_blockgrid.inp)
  draw = antenna(trigger.inp)

class tetris_draw_score(bee.frame):
  scorearea_ = attribute("parent","scorearea")
  scorearea_id_ = attribute("parent","scorearea_id")

  scorestr = dragonfly.std.variable("mstr")("")
  scorecontrol = dragonfly.mutable.mstrcontrol()
  connect(scorestr, scorecontrol)  
  w_draw = dragonfly.canvas.draw3("mstr")(scorearea_id_)
  do_draw = dragonfly.std.transistor("mstr")()
  connect(scorestr, do_draw)
  connect(do_draw, w_draw)
  update = dragonfly.canvas.update3(scorearea_id_)  
  
  set_score = dragonfly.std.transistor("str")()
  connect(set_score, scorecontrol.set)
  set_score_trig = dragonfly.convert.trigger("str")()
  connect(set_score, set_score_trig)
  connect(set_score_trig, update)
  get_score = dragonfly.convert.pull.cast("int","str")()
  connect(get_score, set_score)
  
  start = antenna(do_draw.trig)
  score = antenna(get_score.inp)
  draw = antenna(set_score.trig)

class parameters(object): 
  def __init__(self, **args):
    for a in args: setattr(self, a, args[a])
  
class main(dragonfly.pandahive.pandahive):
  blocks = blocks
  gridx = 10
  gridy = 20  
  mainarea = box2d(100,150,225,375)
  mainarea_id = "main"
  mainarea_parameters = parameters(color=(0.5,0.5,0.5,0))
  scorearea = box2d(170,100,80,40)
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

  c0 = configure("canvas") #must have a lower-alphabet name than "canvas"
  c0.reserve(mainarea_id_,("object","bgrid"), box=mainarea_, parameters = mainarea_parameters_)
  c0.reserve(scorearea_id_,"mstr", box=scorearea_)
  
  maingrid = dragonfly.std.variable(("object","bgrid"))(emptygrid)
  maingridcontrol = dragonfly.grid.bgridcontrol()
  connect(maingrid, maingridcontrol.grid)

  blockgrid = dragonfly.std.variable(("object","bgrid"))(emptygrid)
  blockgridcontrol = dragonfly.grid.bgridcontrol()
  connect(blockgrid, blockgridcontrol.grid)
  
  select_block = tetris_select_block(blocks=blocks_)
  connect(select_block, blockgridcontrol.set)    
  init_main = tetris_init_main(gridx_,gridy_)
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
  
  period = dragonfly.std.variable("float")(0.3)
  cycle = dragonfly.time.cycle()
  connect(period, cycle)
  
  connect(cycle, control.move_down)
  connect(cycle, draw.draw)
  connect(control.dropped, select_block)
  connect(control.dropped, control.place_init)
  connect(control.lost, "exitactuator")

  k_left = dragonfly.io.keyboardsensor_trigger("LEFT")
  connect(k_left, control.move_left)
  connect(k_left, draw.draw)
  k_right = dragonfly.io.keyboardsensor_trigger("RIGHT")
  connect(k_right, control.move_right)
  connect(k_right, draw.draw)

  k_return = dragonfly.io.keyboardsensor_trigger("RETURN")
  connect(k_return, control.rotate_cw)
  connect(k_return, draw.draw)
  k_space = dragonfly.io.keyboardsensor_trigger("SPACE")
  connect(k_space, control.rotate_ccw)
  connect(k_space, draw.draw)

  k_down = dragonfly.io.keyboardsensor_trigger("DOWN")
  connect(k_down, control.drop)
  connect(k_down, draw.draw)

  score = dragonfly.std.variable("int")(0)
  draw_score = tetris_draw_score()
  connect(score, draw_score)
  connect(start, draw_score.start)
  connect(start, draw_score.draw)
  
  reward_block = dragonfly.std.variable("int")(1)
  reward_line = dragonfly.std.variable("int")(10)
  reward_line2 = dragonfly.std.variable("int")(50)
  reward_line3 = dragonfly.std.variable("int")(100)
  reward_line4 = dragonfly.std.variable("int")(200)
  connect(reward_block, control.reward_block)
  connect(reward_line, control.reward_line)
  connect(reward_line2, control.reward_line2)
  connect(reward_line3, control.reward_line3)
  connect(reward_line4, control.reward_line4)

  connect(score, control.score)
  connect(control.newscore, score)
  update_score = dragonfly.convert.trigger("int")()
  connect(control.newscore, update_score)
  connect(update_score, draw_score.draw)

  raiser = bee.raiser()
  connect("evexc", raiser)
  
m = main().getinstance()
m.build("main")
m.place()
m.close()
m.init()
m.run()
