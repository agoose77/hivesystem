from .. import types
from ._runtime_segment import _runtime_segment
import libcontext
import functools

supported_triggered = {
  "push": ("output","default"),
  "pull": ("input","update","default"),
}

class runtime_buffer_builtinpropertyclass(object):
  @staticmethod
  def get(buffername, beeinstance):
    return beeinstance.__variabledict__[buffername].value
  @staticmethod
  def set(buffername, beeinstance, value):
    beeinstance.__variabledict__[buffername].value = value

class runtime_buffer_push(_runtime_segment):
  buffername = None #must be overridden
  startvalue = None
  def __init__(self, beeinstance, beename):
    self.isobject = False
    if isinstance(self.type, str):
      if self.type == "object": 
        self.isobject = True
    elif isinstance(self.type, tuple):
      if len(self.type) and self.type[0] == "object": 
        self.isobject = True    
  
    self.value = self.startvalue  
    if not hasattr(type(beeinstance), self.buffername) or \
     not isinstance(getattr(type(beeinstance), self.buffername), property):        
      prop = property(
        functools.partial(runtime_buffer_builtinpropertyclass.get, self.buffername),
        functools.partial(runtime_buffer_builtinpropertyclass.set, self.buffername),
      )
      setattr(type(beeinstance), self.buffername, prop)
    
    beeinstance.__variabledict__[self.buffername] = self
    
    _runtime_segment.__init__(self, "push", "push", beeinstance, beename)
  def input(self, value):
    self.value = value
  def output(self):
    if self.value is None and not self.isobject: 
      raise ValueError("Buffer segment cannot return None") 
    return self.value

class runtime_buffer_pull(_runtime_segment):
  startvalue = None
  pull_input_socketclass = libcontext.socketclasses.socket_single_optional
  def __init__(self, beeinstance, beename):
    self.isobject = False
    if isinstance(self.type, str):
      if self.type == "object": 
        self.isobject = True
    elif isinstance(self.type, tuple):
      if len(self.type) and self.type[0] == "object": 
        self.isobject = True    

    self.value = self.startvalue  
    prop = property(
      functools.partial(runtime_buffer_builtinpropertyclass.get, self.buffername),
      functools.partial(runtime_buffer_builtinpropertyclass.set, self.buffername),
    )
    setattr(type(beeinstance), self.buffername, prop)
    
    beeinstance.__variabledict__[self.buffername] = self
        
    _runtime_segment.__init__(self, "pull", "pull", beeinstance, beename)
  def input(self, value):
    self.value = value    
  def output(self):
    if self.value is None and not self.isobject: 
      raise ValueError("Buffer segment cannot return None") 
    return self.value

class buffer(object):
  def __init__(self, mode, type):
    mt =  types.mode_type(mode,type)
    self.mode = mt.mode.value
    self.type = mt.type.value
    if mt.type.push_type:
      raise TypeError("Push-specific type %s cannot be used with buffers" % self.type)
    if self.mode == "push":
      self.set_startvalue = self._set_startvalue
    
    self._connection_input = []
    self._connection_output = []
    self._triggering_input = []
    self._triggering_output = []
    self._triggering_update = []
    self._triggering_default = []
    self._triggered_input = []
    self._triggered_output = []
    self._triggered_update = []
    self._triggered_default = []    
    self.startvalue = None    
    for signal in ("input", "output", "update", "default"):
      if signal in supported_triggered[self.mode]:
        setattr(self,"triggered_"+signal, getattr(self, "_triggered_" + signal + "_"))
      setattr(self,"triggering_"+signal, getattr(self, "_triggering_" + signal + "_"))
  def connection_input_type(self):
    return self.mode, self.type    
  def connection_input(self, connection):
    if self.mode == "pull" and len(self._connection_input):
      raise AttributeError("Pull buffers can have only a single input")      
    self._connection_input.append(connection)    
  def connection_output_type(self):
    return self.mode, self.type
  def connection_output(self, connection):
    self._connection_output.append(connection)
  def set_startvalue(self, value):
    self.startvalue = value    
  def _triggering_input_(self, arg):  
    self._triggering_input.append(arg)
  def _triggering_output_(self, arg):  
    self._triggering_output.append(arg)    
  def _triggering_update_(self, arg):  
    self._triggering_update.append(arg)    
  def _triggering_default_(self, arg):  
    self._triggering_default.append(arg)        
  def _triggered_input_(self, arg):  
    self._triggered_input.append(arg)
  def _triggered_output_(self, arg):  
    self._triggered_output.append(arg)    
  def _triggered_update_(self, arg):  
    self._triggered_update.append(arg)    
  def _triggered_default_(self, arg):  
    self._triggered_default.append(arg)            
  def _set_startvalue(self, value):
    self.startvalue = value
  def build(self, segmentname):
    self.segmentname = segmentname
    if self.mode == "push":
      dic = {
        "buffername":segmentname,
        "startvalue":self.startvalue,
        "segmentname":segmentname,        
        "connection_input":self._connection_input,
        "connection_output":self._connection_output,
        "_triggering_input":self._triggering_input+self._triggering_update+self._triggering_output+self._triggering_default,
        "_triggered_output":self._triggered_output+self._triggered_default,
      }      
      return type("runtime_buffer:"+segmentname, (runtime_buffer_push,), dic)
    else:
      dic = {
        "buffername":segmentname,
        "startvalue":self.startvalue,
        "segmentname":segmentname,        
        "connection_input":self._connection_input,
        "connection_output":self._connection_output,
        "_triggering_input":self._triggering_input+self._triggering_update+self._triggering_default,
        "_triggering_output":self._triggering_output,
        "_triggered_input":self._triggered_input+self._triggered_update+self._triggered_default,
      }      
      return type("runtime_buffer:"+segmentname, (runtime_buffer_pull,), dic)
  
