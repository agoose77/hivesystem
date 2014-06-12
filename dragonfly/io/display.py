import bee
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class display(object):
  metaguiparams = {"type_inp": "type"}
  def __new__(cls, type_inp):  
    class display(bee.worker):
      header = variable("str")
      parameter(header, None)    
      inp = antenna("push", type_inp)
      v_inp = variable(type_inp)
      connect(inp, v_inp)
      @modifier
      def display(self):
        if self.header in (None,"None"):
          self.displayfunc(self.v_inp)
        else:
            self.displayfunc(self.header+str(self.v_inp))
      trigger(v_inp, display, "update")
      def set_display(self, displayfunc):
        self.displayfunc = displayfunc
      def place(self):
        libcontext.socket("display", socket_single_required(self.set_display))
    return display

display_str = display("str")

