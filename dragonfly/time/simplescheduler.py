import bee
import libcontext
from libcontext.pluginclasses import *
from libcontext.socketclasses import *

class simplescheduler(bee.drone):
  def __init__(self):
    self.events = []
  def add_event(self, event):
    self.events.append(event)
  def set_eventfunc(self, eventfunc):
    self.eventfunc = eventfunc
  def tick(self, dummyarg=None):
    while len(self.events):
      e = self.events.pop(0)
      self.eventfunc(e)
  def place(self): 
    libcontext.socket(("evin","event"), socket_single_required(self.set_eventfunc))
    libcontext.plugin(("evin","listener"), plugin_single_required(("leader", self.tick, "tick")))
    libcontext.plugin(("evin","scheduler"), plugin_supplier(self))
