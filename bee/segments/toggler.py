from .. import types
from ._runtime_segment import runtime_toggler

class toggler(object):
  def __init__(self, input1, input2):
    self.input1 = types.connection_outputclass(input1)
    self.input2 = types.connection_outputclass(input2)
    self._connection_output = []
          
    self.bound = (self.input1.bound and self.input2.bound) 
    self.typetest()

  def typetest(self):    
    if self.input1.bound:
      inptyp = self.input1.value.connection_output_type()
      inptyp = types.mode_type(*inptyp)      
      if inptyp != types.mode_type("push", "trigger"):
        raise TypeError('Toggler input 1 must be of type ("push", "trigger"), is (%s, %s)' % \
          (inptyp.mode.value, inptyp.type.value))

    if self.input2.bound:
      inptyp = self.input2.value.connection_output_type()
      inptyp = types.mode_type(*inptyp)      
      if inptyp != types.mode_type("push", "trigger"):
        raise TypeError('Toggler input 2 must be of type ("push", "trigger"), is (%s, %s)' % \
          (inptyp.mode.value, inptyp.type.value))
        
  def bind(self, classname, dic):
    if not self.bound:      
      if not self.input1.bound: self.input1.bind(classname, dic)
      if not self.input2.bound: self.input2.bind(classname, dic)
      self.bound = True
      self.typetest()

  def connection_output_type(self):
    return "push", "toggle"
    
  def connection_output(self, connection):
    self._connection_output.append(connection)    

  def connect(self, identifier):
    class toggler_proxy:
      def __init__(self, identifier):
        self.identifier = identifier
    self.identifier = "toggler-"+identifier    
    self.input1.value.connection_output(toggler_proxy(self.identifier+":1"))
    self.input2.value.connection_output(toggler_proxy(self.identifier+":2"))    

  def build(self, segmentname):
    dic = {
      "segmentname":segmentname, 
      "id": self.identifier,       
      "connection_output":self._connection_output,
    }
    return type("runtime_toggler:"+segmentname, (runtime_toggler,), dic)
