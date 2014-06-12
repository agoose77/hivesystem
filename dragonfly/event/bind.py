import libcontext
from bee.bind import *

class eventlistener(binderdrone):
  def __init__(self, leader):
    self.leader = leader
    self.bindnames = set()
    self.send_event = {}
  def listener(self, event):
    for bindname in list(self.bindnames):
      if bindname not in self.binderworker.hives:
        self.bindnames.remove(bindname)
        continue        
      self.send_event[bindname](event)
  def set_send_event(self, send_event):
    self.send_event[self.currbindname] = send_event
  def bind(self, binderworker,bindname):
    self.binderworker = binderworker
    if self.listener not in binderworker.eventfuncs:
      binderworker.eventfuncs.append(self.listener)
    self.bindnames.add(bindname)
    self.currbindname = bindname    
    s = libcontext.socketclasses.socket_single_required(self.set_send_event)
    libcontext.socket(("evin","event"), s)
  def place(self):
    p = libcontext.pluginclasses.plugin_single_required(("match_leader", self.listener, self.leader))
    libcontext.plugin(("evin","listener"), p)

class eventdispatcher(binderdrone):
  def __init__(self):
    self.bindnames = set()
    self.send_event = {}
  def listener(self, event):
    for bindname in list(self.bindnames):
      if bindname not in self.binderworker.hives:
        self.bindnames.remove(bindname)
        continue
      e = event.match_head(bindname)
      if e is not None:
        self.send_event[bindname](e)
  def set_send_event(self, send_event):
    self.send_event[self.currbindname] = send_event
  def bind(self, binderworker,bindname):
    self.binderworker = binderworker
    if self.listener not in binderworker.eventfuncs:
      binderworker.eventfuncs.append(self.listener)
    self.bindnames.add(bindname)
    self.currbindname = bindname    
    s = libcontext.socketclasses.socket_single_required(self.set_send_event)
    libcontext.socket(("evin","event"), s)
  def place(self):
    p = libcontext.pluginclasses.plugin_single_required(("all", self.listener))
    libcontext.plugin(("evin","listener"), p)


class eventforwarder(binderdrone):
  def __init__(self):
    self.bindnames = set()
    self.send_event = {}
  def listener(self, event):
    for bindname in list(self.bindnames):
      if bindname not in self.binderworker.hives:
        self.bindnames.remove(bindname)
        continue        
      self.send_event[bindname](event)
  def set_send_event(self, send_event):
    self.send_event[self.currbindname] = send_event
  def bind(self, binderworker,bindname):
    self.binderworker = binderworker
    if self.listener not in binderworker.eventfuncs:
      binderworker.eventfuncs.append(self.listener)
    self.bindnames.add(bindname)
    self.currbindname = bindname    
    s = libcontext.socketclasses.socket_single_required(self.set_send_event)
    libcontext.socket(("evin","event"), s)
  def place(self):
    p = libcontext.pluginclasses.plugin_single_required(("all", self.listener))
    libcontext.plugin(("evin","listener"), p)

class bind(bind_baseclass):
  dispatch_events = bindparameter("byhead")
  binder("dispatch_events","byhead", eventdispatcher(), "bindname")
  binder("dispatch_events","toall", eventforwarder())
