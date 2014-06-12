try:
  from direct.showbase import DirectObject
  from pandac.PandaModules import *
  import panda3d
  DirectObject = DirectObject.DirectObject
except ImportError:
  panda3d = None
  DirectObject = object

import functools
import bee, libcontext
from libcontext.pluginclasses import *
from libcontext.socketclasses import *

from bee import event

trans = {}
for n in range(0,10):
  trans[str(n)] = str(n)
for n in range(65, 65+27):
  trans[chr(n+32)] = chr(n)
for n in range(1,13): trans["f"+str(n)] = "F"+str(n)
for n in ("escape", "tab", "backspace", "insert", "home", "delete", "space"):
  trans[n] = n.upper()
trans["enter"] = "RETURN"
trans["arrow_up"] = "UP"
trans["arrow_down"] = "DOWN"
trans["arrow_left"] = "LEFT"
trans["arrow_right"] = "RIGHT"

class panda_inputlistener(DirectObject):
  def __init__(self, parent):
    self.parent = parent
    for k in trans:
      f = functools.partial(self.parent.keypressed, trans[k])
      self.accept(k, f)
    f = functools.partial(self.parent.mousebuttonpressed, "LEFT")
    self.accept("mouse1", f)
    f = functools.partial(self.parent.mousebuttonpressed, "RIGHT")
    self.accept("mouse3", f)
    f = functools.partial(self.parent.mousebuttonpressed, "MIDDLE")
    self.accept("mouse2", f)
    f = functools.partial(self.parent.mousebuttonreleased, "LEFT")
    self.accept("mouse1-up", f)
    f = functools.partial(self.parent.mousebuttonreleased, "RIGHT")
    self.accept("mouse3-up", f)
    f = functools.partial(self.parent.mousebuttonreleased, "MIDDLE")
    self.accept("mouse2-up", f)
    f = functools.partial(self.parent.mousewheel, "UP")
    self.accept("wheel_up", f)
    f = functools.partial(self.parent.mousewheel, "DOWN")
    self.accept("wheel_down", f)
    
  def destroy(self):
    self.ignoreAll()

class inputhandler(bee.drone):
  def __init__(self):
    self.targets = []
  def add_target(self, target):
    self.targets.append(target)

  def keypressed(self, key):
    e = event("keyboard","keypressed", key)
    for t in self.targets: t.add_event(e)

  def keyreleased(self, key):
    e = event("keyboard","keyreleased", key)
    for t in self.targets: t.add_event(e)
  
  def get_mouse(self):
    x = 0.5*self.window.mouseWatcherNode.getMouseX()+0.5
    y = -0.5*self.window.mouseWatcherNode.getMouseY()+0.5
    return x,y
  
  def mousebuttonpressed(self, button):
    e = event("mouse","buttonpressed", button, self.get_mouse())
    for t in self.targets: t.add_event(e)

  def mousebuttonreleased(self, button):
    e = event("mouse","buttonreleased", button, self.get_mouse())
    for t in self.targets: t.add_event(e)

  def mousewheel(self, updown):
    e = event("mouse","wheel", updown, self.get_mouse())
    for t in self.targets: t.add_event(e)

  def startup(self):
    self.listener = panda_inputlistener(self)

  def destroy(self):
    self.listener.destroy()
    del self.listener
  
  def get_window(self, window):
    self.window = window
    
  def place(self):
    if panda3d is None: raise ImportError("Cannot locate Panda3D")
    libcontext.socket(("panda","window"), socket_single_required(self.get_window))
    
    libcontext.socket(("evout", "scheduler"), socket_container(self.add_target))
    libcontext.plugin(("evout", ("input", "keyboard")), plugin_flag())
    libcontext.plugin(("evout", ("input", "keyboard", "extended")), plugin_flag())
    libcontext.plugin(("evout", ("input", "keyboard", "keyreleased")), plugin_flag())
    libcontext.plugin(("evout", ("input", "mouse")), plugin_flag())
    libcontext.plugin(("evout", ("input", "mouse", "wheel")), plugin_flag())

    libcontext.plugin(("evout", ("input", "get_mouse")), plugin_supplier(self.get_mouse))
    libcontext.plugin("startupfunction", plugin_single_required(self.startup))
    libcontext.plugin("cleanupfunction", plugin_single_required(self.destroy))    
