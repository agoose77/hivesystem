import bee, bee.segments
import dragonfly, dragonfly.sys
from dragonfly.commandhive import commandhive, commandapp
from dragonfly.io import commandsensor

import os
class make_move(bee.worker):
  move = bee.segments.antenna("push", "str")
  v_move = bee.segments.variable("str")
  bee.segments.connect(move,v_move)
  @bee.segments.modifier
  def m_move(self):
    move = self.v_move[0]
    try:
      gamekeeper.make_move(move)
      gameboard.make_move(move)          
    except ValueError:
      raise ValueError(move)
  bee.segments.trigger(v_move, m_move, "update")

class except_valueerror(bee.worker):
  raisin = bee.segments.antenna("push", "exception")
  v_inp = bee.segments.variable("exception")
  bee.segments.connect(raisin, v_inp)
  @bee.segments.modifier
  def raising(self):    
    if self.v_inp[1][0] == ValueError:       
      print "Invalid move:", self.v_inp[1][1]
      self.v_inp.cleared = True
  bee.segments.trigger(v_inp, raising)


from direct.showbase.ShowBase import taskMgr
from bee import hivemodule

class myapp(commandapp):
  def on_tick(self):
    taskMgr.step()
import libcontext, time

class myhive(commandhive):
  
  commandsensor = commandsensor()
  _hivecontext = hivemodule.appcontext(myapp)
  move = make_move()
  bee.connect(commandsensor, move)

  exc_v = except_valueerror()
  bee.connect(move.evexc, exc_v)

  raiser = bee.raiser() 
  bee.connect("evexc", raiser) 
      
m = myhive().getinstance()
m.build("m")
m.place()
m.close()

m.init()

from components import chesskeeper, chessboard

from panda3d.core import getModelPath
import os
getModelPath().prependPath(os.getcwd())

gamekeeper = chesskeeper.chesskeeper()
gamekeeper.new()

def movefunc(move):
  from bee.event import event
  m.move.v_move = event(move)
  m.move.m_move()
  print move

class mygameboard(chessboard.chessboard):
  def move(self, move):
    movefunc(move)
  
gameboard = mygameboard()
  
m.run()

