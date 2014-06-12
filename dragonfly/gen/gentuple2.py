import bee
from bee.segments import *
import functools

class gentuple2(object):
  """
  Wraps a tuple or other iterable
  Provide an unresolved tuple
  """
  def __new__(cls,wrapped_tuple):
    class gentuple2(bee.worker):  
      def set_parent(self, parent):
        self.parent = parent
      def resolve(self, wrapped):
        return bee.resolve(wrapped, parent=self.parent)
     
      v_wrapped = variable(("object","iterable","tuple"))
      startvalue(v_wrapped, wrapped_tuple)
      value = output("pull",("object","iterable","tuple"))
      connect(v_wrapped, value)
      @modifier
      def m_value(self):
        self.v_wrapped = self.resolve(wrapped_tuple)
      pretrigger(v_wrapped, m_value)
      
      def get_value(self):
        return self.resolve(wrapped_tuple)
      
      @staticmethod
      def worker_length():
         class length(bee.worker):
           v_length = variable("int")           
           @modifier
           def m_length(self):
             self.v_length = len(self.resolve(wrapped_tuple))
           outp = output("pull","int")
           connect(v_length, outp)
           pretrigger(v_length, m_length)
         return length()  
      @staticmethod
      def worker_item(index):
         class item(bee.worker):
           v_item = variable("object")           
           @modifier
           def m_item(self):
             self.v_item = self.resolve(wrapped_tuple)[index]
           outp = output("pull","object")
           connect(v_item, outp)
           pretrigger(v_item, m_item)
         return item()  
      @staticmethod
      def worker_getitem():
         class getitem(bee.worker):
           inp = antenna("pull","int")
           b_inp = buffer("pull","int")
           trig_inp = triggerfunc(b_inp, "update")
           connect(inp, b_inp)
           outp = output("pull","object")
           v_outp = variable("object")           
           connect(v_outp, outp)
           @modifier
           def m_getitem(self):
             self.trig_inp()
             index = self.b_inp
             item = self.resolve(wrapped_tuple)[index]
             self.v_outp = item
           pretrigger(v_outp, m_getitem)
         return getitem()  
      @staticmethod
      def worker_slice(start,end):
         class slice(bee.worker):
           v_slice = variable(("object","iterable","tuple"))           
           @modifier
           def m_slice(self):
             self.v_slice = self.resolve(wrapped_tuple)[start:end]
           outp = output("pull",("object","iterable","tuple"))
           connect(v_slice, outp)
           pretrigger(v_slice, m_slice)           
         return slice()  
      @staticmethod
      def worker_getslice():
         class getslice(bee.worker):
           inp = antenna("pull",("int","int"))
           b_inp = buffer("pull",("int","int"))
           trig_inp = triggerfunc(b_inp, "update")
           connect(inp, b_inp)
           outp = output("pull",("object","iterable","tuple"))
           v_outp = variable(("object","iterable","tuple"))           
           connect(v_outp, outp)
           @modifier
           def m_getslice(self):
             self.trig_inp()
             start,end = self.b_inp
             slice = self.resolve(wrapped_tuple)[start:end]
             self.v_outp = slice
           pretrigger(v_outp, m_getslice)
         return getslice()  
    return gentuple2()
