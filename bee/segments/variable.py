from __future__ import print_function

from .. import types
from ._runtime_segment import _runtime_segment
import functools

class runtime_variable_builtinpropertyclass(object):
  @staticmethod
  def get(variablename, beeinstance):
    return beeinstance.__variabledict__[variablename].variablevalue
  @staticmethod
  def set(variablename, beeinstance, value):
    beeinstance.__variabledict__[variablename].variablevalue = value
  
  
class runtime_variable(_runtime_segment):
  variablename = None #must be overridden
  startvalue = None
  def __init__(self, beeinstance, beename):
    self.isobject = False
    if isinstance(self.type, str):
      if self.type == "object": 
        self.isobject = True
    elif isinstance(self.type, tuple):
      if len(self.type) and self.type[0] == "object": 
        self.isobject = True    

    self.variablevalue = self.startvalue
  
    if not hasattr(type(beeinstance), self.variablename) or \
     not isinstance(getattr(type(beeinstance), self.variablename), property):    
      prop = property(
        functools.partial(runtime_variable_builtinpropertyclass.get, self.variablename),
        functools.partial(runtime_variable_builtinpropertyclass.set, self.variablename),
      )
      setattr(type(beeinstance), self.variablename, prop)
    
    beeinstance.__variabledict__[self.variablename] = self
    _runtime_segment.__init__(self, "push","pull", beeinstance, beename)
  def input(self, value):
    self.variablevalue = value
  def output(self):
    if self.variablevalue is None and not self.isobject: 
      raise ValueError("Variable segment cannot return None") 
    return self.variablevalue  
  
class variable(object):
  def __init__(self, type):
    self.type = types.typeclass(type)
    if self.type.push_type:
      raise TypeError("Push-specific type %s cannot be used with properties" % self.type.value)    
    self.type = self.type.value      
    self._connection_input = []
    self._connection_output = []
    self._triggering_input = []
    self._triggering_output = []
    self._triggering_update = []
    self._triggering_default = []    
    self.startvalue = None
  def connection_input_type(self):
    return "push", self.type
  def connection_input(self, connection):
    self._connection_input.append(connection)    
  def connection_output_type(self):
    return "pull", self.type
  def connection_output(self, connection):
    self._connection_output.append(connection)
  def set_startvalue(self, value):
    self.startvalue = value
  def triggering_input(self, arg):  
    self._triggering_input.append(arg)
  def triggering_output(self, arg):  
    self._triggering_output.append(arg)    
  def triggering_update(self, arg):  
    self._triggering_update.append(arg)    
  def triggering_default(self, arg):  
    self._triggering_default.append(arg)        
  def build(self, segmentname):
    self.segmentname = segmentname
    dic = {
      "variablename":segmentname,            
      "segmentname":segmentname,
      "startvalue":self.startvalue,
      "connection_input":self._connection_input,
      "connection_output":self._connection_output,
      "_triggering_input":self._triggering_input+self._triggering_update+self._triggering_default,
      "_triggering_output":self._triggering_output,
    }
    return type("runtime_variable:"+segmentname, (runtime_variable,), dic)
