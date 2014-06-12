from ._io_base import io_base
import libcontext
from ._runtime_segment import tryfunc

class _runtime_antenna_blockcontrol(object):
  segmentname = None
  antenna_push_plugin = None
  def __init__(self, beeinstance, beename):
    self.beename = beename
    self.beeinstance = beeinstance
    self.input = self._input
    self._blockcontrol = None
    setattr(beeinstance, self.segmentname, self)    
  def set_blockcontrol(self, blockcontrol):
    self._blockcontrol = blockcontrol
  def set_catchfunc(self, catchfunc):  
    self.input = tryfunc(catchfunc, self.input)      
  def _input(self):
    if self._blockcontrol is None: raise ValueError
    return self._blockcontrol()
  def place(self):
    pluginclass = libcontext.pluginclasses.plugin_supplier
    self.antenna_push_plugin = pluginclass(self.input)
    libcontext.plugin(("bee", "antenna", self.segmentname, "blockcontrol"), self.antenna_push_plugin)

class antenna_blockcontrol(io_base):
  def __init__(self):
    pass
  def guiparams(self, segmentname, guiparams):
    pnam = "antennas"
    if pnam not in guiparams:
      guiparams[pnam] = {}
    p = ("push", "blockcontrol")
    guiparams[pnam][segmentname] = p
  def build(self, segmentname):
    self.segmentname = segmentname
    dic = {      
      "segmentname": segmentname,
    }
    return type("runtime_antenna_blockcontrol:"+segmentname, (_runtime_antenna_blockcontrol,), dic)
