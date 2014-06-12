"""
The complex scheduler has the following extra features 
- add_event has an additional optional priority argument;
  high priority events happen sooner
- add_event_delay: additional arguments "mode" and "delay"
  mode "ticks": "delay" indicates the number of ticks that must be waited.
    0 means the event will be processed in the next tick, 1 in the tick after that, etc.
  mode "time": "delay" indicates the delay in seconds
    0 means the event will be processed immediately
  
"""

#UNTESTED!

from .simplescheduler import simplescheduler

import libcontext
from libcontext.pluginclasses import *
from libcontext.socketclasses import *

import bisect

class complexscheduler(simplescheduler):
  def __init__(self):
    self.eventkeys = []
    self.events = []
  def tick(self, dummyarg=None):    
    loop = True
    while loop:
      for enr,e in enumerate(self.events):
        if e[2] != None:
          mode, value = e[2]
          if mode == "ticks" and value <= self.pacemaker.count: continue
          if mode == "time" and value < self.pacemaker.time: continue
          self.events.pop(enr)
        self.eventkeys.pop(enr)        
        self.eventfunc(e)
        break          
      else:
        loop = False
  def add_event(self, event, priority = 0):
    point = bisect.bisect_left(self.eventkeys, priority)
    self.eventkeys.insert(point, priority)
    self.events.insert(point,(event, priority, None))    
  def add_event_delay(self, event, mode, delay, priority = 0):
    assert delay >= 0, delay
    assert mode in ("ticks", "time"), mode
    if mode == "ticks": value = self.pacemaker.count+delay
    elif mode == "time": value = self.pacemaker.time+delay
    point = bisect.bisect_left(self.eventkeys, priority)
    self.eventkeys.insert(point, priority)
    self.events.insert(point,(event, priority, (mode, value)))        
  def set_pacemaker(self, pacemaker):
    self.pacemaker = pacemaker
  def place(self):
    simplescheduler.place.im_func(self)  
    libcontext.socket("pacemaker", socket_single_required(self.set_pacemaker))
    libcontext.plugin(("evin","scheduler", "complex"), plugin_flag())
