import threading, libcontext, bee, time
from ..consolehive.getch import *
from ..keycodes import *
from libcontext.pluginclasses import *
from libcontext.socketclasses import *
from bee import event

try:
  raw_input = raw_input
except NameError:
  raw_input = input
    
class inputhandler(bee.drone):
  def __init__(self):
    self.targets = []
  def add_target(self, target):
    self.targets.append(target)
  def set_new_command(self, new_command):
    self.new_command = new_command
  def startup(self):
    def gcom(event, addcomfunc):
      while not event.is_set():
        try:
          com = raw_input(">>>")
          if com != None:
            addcomfunc(com)
            time.sleep(0.2)
        except EOFError:
          pass
    change_termios()
    self.dead = threading.Event()
    t = threading.Thread(target=gcom, args=(self.dead, self.new_command,))  
    t.daemon = True
    t.start()
  def restore_terminal(self):
    self.dead.set()
    restore_termios()
  def place(self):
    libcontext.plugin(("evout", ("input", "command")), plugin_flag())
    libcontext.socket(("evout", "scheduler"), socket_container(self.add_target))
    libcontext.socket(("command", "new_command"), socket_single_required(self.set_new_command))
    libcontext.plugin("startupfunction", plugin_single_required(self.startup))
    libcontext.plugin("cleanupfunction", plugin_single_required(self.restore_terminal))    
    
