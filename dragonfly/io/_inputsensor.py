import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *

# keyboard: trigger, pulse (tick-driven only) and impulse (real-time only)
#in case of pulse, add a new event at next tick
#in case of impulse, add a new event at a very small delay, 
# so that it gets processed at the next frame

"""
If the keycode must be changed, simply disable the sensor and build a new one.
"""


class keyboardsensor_base(bee.worker):
    def set_add_listener(self, add_listener):
        self.add_listener = add_listener

    def set_remove_listener(self, remove_listener):
        self.remove_listener = remove_listener

    def place(self):
        libcontext.socket(("evin", ("input", "keyboard")), socket_flag())
        libcontext.socket(("evin", "add_listener"), socket_single_required(self.set_add_listener))
        libcontext.socket(("evin", "remove_listener"), socket_single_required(self.set_remove_listener))
        libcontext.plugin(("bee", "init"), plugin_single_required(self.enable))

    def enable(self):
        pass

    def disable(self):
        pass


"""    
class keyboardsensor_pulse(keyboardsensor_base):
  keycode = variable("str")
  Parameter(keycode, "SPACE")

  def __init__(self, keycode):
    self.pulses = []
    keyboardsensor_base.__init__(self, keycode)
    self.pressed = False
  def _pulse(self, channel, message):
    count = 1
    if channel[1] == "keyreleased" and self.pressed == False: count = 2
    if channel[1] == "keypressed" and self.pressed == True: count = 2
    for n in range(count):
      for p in self.pulses: p()    
      self.pressed = not self.pressed
  def add_pulse(self, pulse):
    assert callable(pulse)
    self.pulses.append(pulse)
  def place(self):
    libcontext.socket("eventhandler", socket_single_required(self.set_eventhandler))  
    libcontext.socket(("input", "keyboard", "keyreleased"), socket_flag())
    if self.keycode not in asciilist:
      libcontext.socket(("input", "keyboard", "extended"), socket_flag())
    libcontext.socket("pulse", socket_supplier(self.add_pulse))
    keyboardsensor_base.place(self)    
  def enable(self):
    self.eventhandler.new_processor(("keyboard", "keypressed", self.keycode), self._pulse)
    self.eventhandler.new_processor(("keyboard", "keyreleased", self.keycode), self._pulse)
  def disable(self):
    self.eventhandler.remove_processor(("keyboard", "keypressed", self.keycode), self._pulse)
    self.eventhandler.remove_processor(("keyboard", "keyreleased", self.keycode), self._pulse)
"""


class mousesensor_base(bee.worker):
    def set_add_listener(self, add_listener):
        self.add_listener = add_listener

    def set_remove_listener(self, remove_listener):
        self.remove_listener = remove_listener

    def place(self):
        libcontext.socket(("evin", ("input", "mouse")), socket_flag())
        libcontext.socket(("evin", "add_listener"), socket_single_required(self.set_add_listener))
        libcontext.socket(("evin", "remove_listener"), socket_single_required(self.set_remove_listener))
        libcontext.plugin(("bee", "init"), plugin_single_required(self.enable))

    def enable(self):
        pass

    def disable(self):
        pass

    def __del__(self):
        self.disable()


"""
class mousebuttonsensor_pulse(mousebuttonsensor_base):
  #TODO
  def place(self):
    mousebuttonsensor_base.place(self)    
"""
