"""
A pacemaker provides the following attributes:
- start_time: the time at the first tick
- time: the time at the last (current) tick
- ticks: the number of ticks passed (0 at the first tick)
"""

import libcontext, bee, time
from libcontext.socketclasses import *
from libcontext.pluginclasses import *

from .pacemaker_simple import pacemaker_simple

class pacemaker_tick(pacemaker_simple):
  def __init__(self, interval):
    self.interval = interval #interval in seconds
  def tick(self):
    t = time.time()
    if self.first:
      self.first = False
      self.ticks = 0
      self.start_time = t
      self.time = t    
      self.eventfunc(bee.event("start"))
    while t - self.start_time > self.interval * self.ticks:
      self.eventfunc(bee.event("tick"))
      self.time = t
      self.ticks += 1
      t = time.time()
  
