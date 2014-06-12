import bee
from bee.segments import *
import bee.segments.weaver

builtin_type = type

class weaver(object):
  metaguiparams = {"type":"type"}
  def __new__(cls, type):
    if not isinstance(type, str) and not isinstance(type, tuple):
      raise AssertionError("Weaver type must be tuple, not '%s'" % builtin_type(type))
    typetuple = type
    if isinstance(type, str): typetuple = (type,)    
    class weaver(bee.worker):
      inputs = []
      n = None
      for n,subtype in enumerate(typetuple):
        nn = str(n+1)
        inp = antenna("pull", subtype)
        inputs.append(inp)
        locals()["inp"+nn] = inp
      del n,subtype,nn,inp
      w = bee.segments.weaver(type, *inputs)
      del inputs      
      outp = output("pull", type)
      connect(w, outp)
    return weaver
      
  

