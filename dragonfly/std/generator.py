import bee
from bee.segments import *

class generator(object):
  metaguiparams = {"type":"type","generator":"object"}
  def __new__(cls, type, generator):
    genfunc = generator
    class generator(bee.worker):  
      gen = None
      outp = output("pull", type)
      v_outp = variable(type)
      connect(v_outp, outp)
      @modifier
      def generate(self):
        if self.gen is None: 
          self.gen = genfunc()
        self.v_outp = next(self.gen)
      pretrigger(v_outp,generate)
    return generator
