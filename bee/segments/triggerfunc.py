from .. import types
from ._helpersegment import helpersegment
from ._runtime_segment import _runtime_triggerfunc

class triggerfunc(helpersegment):
  def __init__(self, target, mode="default"):
    self.target = types.triggered_class(target, mode)
    self.bound = self.target.bound
  def bind(self, classname, dic):
    if not self.bound:
      self.target.bind(classname, dic)
  def connect(self, identifier):
    self.identifier = identifier
    attr = "triggered_" + self.target.mode
    getattr(self.target.value, attr)(self)
  def build(self, segmentname):
    assert segmentname == self.identifier
    dic = {
      "segmentname":segmentname
    }
    return type("runtime_triggerfunc:"+segmentname, (_runtime_triggerfunc,), dic)
    
