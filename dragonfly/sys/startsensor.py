from bee import *
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *

class startsensor(worker):
  outp = output("push", "trigger")
  start = triggerfunc(outp)
  #def set_add_listener(self, add_listener):
  #  self.add_listener = add_listener 
  #def init(self):
  #  def do_start(event):
  #    self.start()
  #  self.add_listener("leader", do_start, "start")
  def place(self):
    #libcontext.socket(("evin", "add_listener"), socket_single_required(self.set_add_listener))
    #libcontext.plugin(("bee", "init"), plugin_single_required(self.init))
    listener = plugin_single_required(("trigger", self.start, "start"))
    libcontext.plugin(("evin", "listener"), listener)
