import bee
from bee.segments import *

class wset(object):
  metaguiparams = {"type":"type"}
  def __new__(cls, type):
    class wset(bee.worker):

      def place(self):
        self.value = set() 

      wset = output("pull", ("object", "set"))
      value = variable(("object", "set"))
      connect(value, wset)

      add = antenna("push", type)
      v_add = variable(type)
      connect(add, v_add)
      @modifier
      def do_add(self):
        self.value.add(self.v_add)
      trigger(v_add, do_add)

      remove = antenna("push", type)
      v_remove = variable(type)
      connect(remove, v_remove)
      @modifier
      def do_remove(self):
        self.value.remove(self.v_remove)
      trigger(v_remove, do_remove)
      
    return wset

    