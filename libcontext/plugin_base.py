from .context import plugincontextdict, socketcontextdict
from .context import pluginnamedict, socketnamedict
from .context import matchreport

class plugin_base:
  def __init__(self, *args, **kargs):
    self.args = args
    self.kargs = kargs
    self.counter = 0
  def __fill__(self, socket):
    pname = pluginnamedict[self]
    sname = socketnamedict[socket]
    pcontext = plugincontextdict[self]
    scontext = socketcontextdict[socket]
    matchreport(scontext, sname, pcontext, pname)
    self.counter += 1    

