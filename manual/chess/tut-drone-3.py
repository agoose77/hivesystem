import bee
import dragonfly
from dragonfly.commandhive import commandhive, commandapp

from components.drones.keyboardmove import keyboardmove
from components.drones.chessprocessor import chessprocessor
from components.drones.chesskeeper import chesskeeper
from components.drones.chessboard import chessboard
from components.drones.movereporter import movereporter
from components.drones.chessUCI import chessUCI


from direct.showbase.ShowBase import taskMgr

from panda3d.core import getModelPath
import os
getModelPath().prependPath(os.getcwd())

from bee import hivemodule

class myapp(commandapp):
  def on_tick(self):
    taskMgr.step()
    taskMgr.step()


class myhive(commandhive):
  _hivecontext = hivemodule.appcontext(myapp)

  keyboardmove("White")
  chessUCI("Black","glaurung")
  chessprocessor()
  chesskeeper()
  chessboard("White")
  movereporter()
        
m = myhive().getinstance()
m.build("m")
m.place()
m.close()

m.init()

m.run()

