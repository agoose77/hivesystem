from ._helpersegment import helpersegment
from .. import types
from ..types import get_parameterclass

class parameter(helpersegment):
  def __init__(self, target, gui_defaultvalue="no-defaultvalue"):
    self.target = types.startvalueclass(target)
    self.gui_defaultvalue = gui_defaultvalue
    self.bound = self.target.bound
  def bind(self, classname, dic):
    if not self.bound:
      self.target.bind(classname, dic)
    self.typename = self.target.value.connection_input_type()[1]
    self.parameterclass = get_parameterclass(self.typename)
    if self.gui_defaultvalue not in (None, "no-defaultvalue"):
      self.gui_defaultvalue = self.parameterclass[1](self.gui_defaultvalue)
  def guiparams(self, segmentname, guiparamsdict):
    self.segmentname = self.target.value.segmentname    
    if "parameters" not in guiparamsdict:
      guiparamsdict["parameters"] = {}
    d = guiparamsdict["parameters"]
    v = None
    if self.gui_defaultvalue !="no-defaultvalue": v=self.gui_defaultvalue
    d[self.segmentname] = (self.parameterclass, v)
  def parameters(self,segmentname):
    return (self.segmentname, self.parameterclass, self.gui_defaultvalue)
    
