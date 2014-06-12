import bee
from bee.segments import *
import libcontext
from libcontext.socketclasses import *

class show3(object):
  metaguiparams = {"type":"type"}
  def __new__(cls, type):
    class show3(bee.worker):
      identifier = variable("id")
      parameter(identifier)
      inp = antenna("push", type)
      v_inp = variable(type)
      connect(inp, v_inp)
      @modifier
      def m_show(self):
        self.show(self.v_inp, self.identifier)
      trigger(v_inp, m_show)
      def set_show(self, showfunc):
        self.show = showfunc
      def place(self):
        s = socket_single_required(self.set_show)
        libcontext.socket(("canvas","show2",type), s)
    return show3

