from __future__ import print_function

import bee
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *

class maindrone(bee.drone):
  def keypress(self, key):
    if key == "W":
      i = "walk"
      self.action1.animplay(i)
      self.action1.soundplay(i)
    elif key == "TAB":
      i = "jump"
      self.action1.animplay(i)
      self.action1.soundplay(i)
    elif key == "R":
      self.action2.actionplay("run")
    elif key == "SPACE":
      self.action2.actionplay("shoot")
    elif key == "S":
      i = "swim"
      self.action3.animplay(i)
      self.action3.soundplay(i)
    elif key == "C":
      i = "crouch"
      self.action3.animplay(i)
      self.action3.soundplay(i)
               
  def start(self):
    print("START")
  def set_action1(self, action1):
    self.action1 = action1
  def set_action2(self, action2):
    self.action2 = action2
  def set_action3(self, action3):
    self.action3 = action3
  def place(self):
    s = socket_single_required(self.set_action1)
    libcontext.socket("action1", s)
    s = socket_single_required(self.set_action2)
    libcontext.socket("action2", s)
    s = socket_single_required(self.set_action3)
    libcontext.socket("action3", s)
  

  
