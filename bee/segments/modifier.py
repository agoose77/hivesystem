from .. import types
from ._decoratorsegment import decoratorsegment
from ._runtime_segment import _runtime_modifier

class modifier(decoratorsegment):
  def __init__(self, decorated):
    assert hasattr(decorated, "__call__")
    self.decorated = decorated
    self._triggered_default = []    
  def triggered_default(self, arg):  
    self._triggered_default.append(arg)            
  def build(self, segmentname):
    dic = {
      "decorated":(self.decorated,),
      "segmentname":segmentname,        
      "_triggered":self._triggered_default,
    }
    return type("runtime_modifier:"+segmentname, (_runtime_modifier,), dic)    
