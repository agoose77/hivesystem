from ._helpersegment import helpersegment
from .. import types

class startvalue(helpersegment):
  def __init__(self, target, value):
    self.target = types.startvalueclass(target)
    self.value = value
    self.bound = self.target.bound
  def bind(self, classname, dic):
    if not self.bound:
      self.target.bind(classname, dic)
  def connect(self, identifier):
    unnamed = [types.get_parameterclass(self.target.value.type)]
    paramvalue = types.parse_parameters(unnamed, [], (self.value,), [])
    self.target.value.set_startvalue(paramvalue[0][0])
