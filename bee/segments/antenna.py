from ._io_base import io_base
from .. import types
from ._runtime_segment import _runtime_antenna_push, _runtime_antenna_pull

class antenna(io_base):
  def __init__(self, mode, type):
    mt =  types.mode_type(mode,type)
    self.mode = mt.mode.value
    self.type = mt.type.value
    self._connection = []
    if self.type in ("trigger", "toggle"): 
      self.triggering_input = self.connection_output_trigger   
      self.triggering_output = self.connection_output_trigger
      self.triggering_default = self.connection_output_trigger
  def connection_output_type(self):
    return self.mode, self.type
  def connection_output(self, connection):
    self._connection.append(connection)
  def connection_output_trigger(self, connection):
    self._connection.append(connection[0])    
  def guiparams(self, segmentname, guiparams):
    pnam = "antennas"
    if pnam not in guiparams:
      guiparams[pnam] = {}
    p = (self.mode, self.type)
    guiparams[pnam][segmentname] = p
  def build(self, segmentname):
    self.segmentname = segmentname
    if self.mode == "push":
      dic = {      
        "_connection": self._connection,
        "segmentname": segmentname,
        "type": self.type,
        "istrigger":(self.type in ("trigger", "toggle")),
      }
      return type("runtime_antenna_push:"+segmentname, (_runtime_antenna_push,), dic)
    elif self.mode == "pull":
      dic = {      
        "_connection": self._connection,
        "segmentname": segmentname,
        "type": self.type,
      }
      return type("runtime_antenna_pull:"+segmentname, (_runtime_antenna_pull,), dic)
    else: 
      raise ValueError()
