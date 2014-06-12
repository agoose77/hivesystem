from .. import types
from ._runtime_segment import _runtime_test
import libcontext

class test(object):
  def __init__(self, input):
    self.input = types.connection_outputclass(input)
    self._connection_output = []
          
    self.bound = self.input.bound
    self.typetest()
    
    self.triggering_input = self.connection_output_trigger   
    self.triggering_output = self.connection_output_trigger
    self.triggering_default = self.connection_output_trigger    

  def typetest(self):        
    if self.input.bound:
      inptyp = self.input.value.connection_output_type()
      inptyp = types.mode_type(*inptyp)      
      if inptyp != types.mode_type("push", "bool"):
        raise TypeError('Test input must be of type ("push", "bool"), is ("%s", "%s")' % \
          (inptyp.mode.value, inptyp.type.value))

  def bind(self, classname, dic):
    if not self.bound:      
      self.input.bind(classname, dic)
      self.bound = True
      self.typetest()

  def connection_output_type(self):
    return "push", "trigger"

  def connection_output(self, connection):
    self._connection_output.append(connection)

  def connection_output_trigger(self, connection):
    self._connection_output.append(connection[0])    

  def connect(self, identifier):
    self.identifier = "test-"+identifier    
    self.input.value.connection_output(self)

  def build(self, segmentname):
    dic = {
      "segmentname":segmentname,        
      "connection_output":self._connection_output,
      "identifier":self.identifier,
    }      
    return type("runtime_test:"+segmentname, (_runtime_test,), dic)
