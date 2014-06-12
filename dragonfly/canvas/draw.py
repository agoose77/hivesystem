import bee
from bee.segments import *
import libcontext
from libcontext.socketclasses import *

class draw(object):
  metaguiparams = {"type":"type"}
  def __new__(cls, type):
    inptype = (type, ("object", "box2d"), "object")
    class draw(bee.worker):
      inp = antenna("push", inptype)
      v_inp = variable(inptype)
      connect(inp, v_inp)
      @modifier
      def m_draw(self):
        obj, bbox, params = self.v_inp
        identifier = self.draw(obj, bbox, params)
        self.v_outp = identifier
      trigger(v_inp, m_draw)
      outp = output("pull", "id")
      v_outp = variable("id") 
      connect(v_outp, outp)
      def set_draw(self, drawfunc):
        self.draw = drawfunc
      def place(self):
        s = socket_single_required(self.set_draw)
        libcontext.socket(("canvas","draw1",type), s)
    return draw

