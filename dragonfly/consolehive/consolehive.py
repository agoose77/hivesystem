from __future__ import print_function
import time

import bee
from bee import hivemodule

import libcontext
from libcontext.pluginclasses import *
from libcontext.socketclasses import *

from . import inputhandler

class inputhandlerhive(bee.frame):
  inputhandler.inputhandler()

class consoleapp(bee.drone):
  def __init__(self):
    self.startupfunctions = []
    self.cleanupfunctions = []
    self.doexit = False
  def on_tick(self):
    pass    
  def run(self):
    try:
      self.finished = False  
      for f in self.startupfunctions: f()
      while not self.doexit: 
        self.pacemaker.tick()
        self.on_tick()
        time.sleep(0.005)        
    finally:
      self.cleanup()
  def exit(self):
    self.doexit = True
  def addstartupfunction(self,startupfunction):
    assert hasattr(startupfunction, "__call__")
    self.startupfunctions.append(startupfunction)    
  def addcleanupfunction(self,cleanupfunction):
    assert hasattr(cleanupfunction, "__call__")
    self.cleanupfunctions.append(cleanupfunction)        
  def cleanup(self):
    if self.finished == False:
      for f in self.cleanupfunctions: f()
    self.finished = True
  def display(self, arg):
    print(arg)
  def watch(self, *args):
    for a in args: print (a,end="")
    print()
  def set_pacemaker(self, pacemaker):
    self.pacemaker = pacemaker
  def place(self): 
    libcontext.socket("startupfunction", socket_container(self.addstartupfunction))
    libcontext.socket("cleanupfunction", socket_container(self.addcleanupfunction))
    libcontext.plugin("exit", plugin_supplier(self.exit))
    libcontext.plugin("stop", plugin_supplier(self.exit))    
    libcontext.plugin("display", plugin_supplier(self.display))
    libcontext.plugin("watch", plugin_supplier(self.watch))
    libcontext.socket("pacemaker", socket_single_required(self.set_pacemaker))
    libcontext.plugin("doexit",plugin_supplier(lambda: getattr(self,"doexit")))

from bee import connect
from ..time import simplescheduler
from ..sys import exitactuator
from ..io import keyboardsensor_trigger
from ..time import pacemaker_simple

class consolehive(bee.inithive):
  _hivecontext = hivemodule.appcontext(consoleapp)
  inputhandler = inputhandlerhive()
  connect(("inputhandler","evout"), "evin")
  scheduler = simplescheduler()
  exitactuator = exitactuator()
  keyboardsensor_exit = keyboardsensor_trigger("ESCAPE")
  pacemaker = pacemaker_simple()
  connect("keyboardsensor_exit", "exitactuator")
