import bee
from bee.segments import *

class iterator(object):
  metaguiparams = {"type":"type"}
  def __new__(cls, type):
    class iterator(bee.worker):  
      iterator = None
      iterable = variable(("object","iterable")) 
      parameter(iterable)
      outp = output("pull", type)
      v_outp = variable(type)
      connect(v_outp, outp)
      def make_iterator(self):
        for v in self.iterable:
          yield v
      @modifier
      def iterate(self):
        if self.iterator is None: self.iterator = self.make_iterator()
        self.v_outp = self.iterator.next()
      pretrigger(v_outp,iterate)
    return iterator
