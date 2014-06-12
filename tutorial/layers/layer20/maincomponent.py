from __future__ import print_function

class maincomponent(object):
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


  
