from __future__ import print_function

import bee
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *

class mainworker(bee.worker):
  action1_anim = output("push", "id")
  action1_sound = output("push", "id")
  action2 = output("push", "id")
  action3_anim = output("push", "id")
  action3_sound = output("push", "id")

  b1_anim = buffer("push","id")
  connect(b1_anim, action1_anim)
  trig_b1_anim = triggerfunc(b1_anim)
  b1_sound = buffer("push","id")
  connect(b1_sound, action1_sound)
  trig_b1_sound = triggerfunc(b1_sound)
  
  b2 = buffer("push","id")
  connect(b2, action2)
  trig_b2 = triggerfunc(b2)
  
  b3_anim = buffer("push","id")
  connect(b3_anim, action3_anim)
  trig_b3_anim = triggerfunc(b3_anim)
  b3_sound = buffer("push","id")
  connect(b3_sound, action3_sound)
  trig_b3_sound = triggerfunc(b3_sound)
  
  def keypress(self, key):
    if key == "W":
      i = "walk"
      self.b1_anim = i
      self.trig_b1_anim()
      self.b1_sound = i
      self.trig_b1_sound()
    elif key == "TAB":
      i = "jump"
      self.b1_anim = i
      self.trig_b1_anim()
      self.b1_sound = i
      self.trig_b1_sound()
    elif key == "R":
      self.b2 = "run"
      self.trig_b2()
    elif key == "SPACE":
      self.b2 = "shoot"
      self.trig_b2()
    elif key == "S":
      i = "swim"
      self.b3_anim = i
      self.trig_b3_anim()
      self.b3_sound = i
      self.trig_b3_sound()
    elif key == "C":
      i = "crouch"
      self.b3_anim = i
      self.trig_b3_anim()
      self.b3_sound = i
      self.trig_b3_sound()
               
  def start(self):
    print("START")


  
