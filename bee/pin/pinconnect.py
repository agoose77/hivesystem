import libcontext, libcontext.pluginclasses

from ..drone import drone
from .inputpin import inputpin
from .outputpin import outputpin
from ..types import typecompare

class pinconnect(drone):
  def __init__(self):
    self.connections = {}
  def __call__(self, source, target):
    if (source, target) in self.connections: return
    ok = False
    while 1:
      if not hasattr(source, "__workerclass__"): break
      wsource = source.__workerclass__
      if isinstance(wsource, tuple): break
      if not hasattr(wsource, "__metabee__"): break
      if isinstance(wsource.__metabee__, tuple): break
      if wsource.__metabee__ != outputpin: break
      ok = True
      break
    if not ok: raise TypeError("Cannot connect pins: first argument is not an outputpin")

    ok = False
    while 1:
      if not hasattr(target, "__workerclass__"): break
      wtarget = target.__workerclass__
      if isinstance(wtarget, tuple): break
      if not hasattr(wtarget, "__metabee__"): break
      if isinstance(wtarget.__metabee__, tuple): break
      if wtarget.__metabee__ != inputpin: break
      ok = True
      break
    if not ok: raise TypeError("Cannot connect pins: second argument is not an inputpin")
    
    
    if source.__pinmode__ != target.__pinmode__:
      raise TypeError("Cannot connect pins: push/pull modes do not match")
    if not typecompare(source.__pintype__, target.__pintype__):
      raise TypeError("Cannot connect pins: types %s and %s do not match" % (source.__pintype__, target.__pintype__))
    
    if source.__pinmode__ == "push":
      if source.__pintype__ == "trigger":
        con = lambda: setattr(target, "value",  True)
      else:
        con = functools.partial(setattr, target, "value")
      source._add_output(con)
    else:
      con = lambda: source.value       
      target._set_input(con)
    self.connections[source,target] = con
  def place(self):
    p = libcontext.pluginclasses.plugin_supplier(self)
    libcontext.plugin(("pin","connect"), p)
      
