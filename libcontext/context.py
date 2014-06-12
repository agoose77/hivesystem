from __future__ import print_function

maxtup = (99999,)*999

from weakref import WeakKeyDictionary,WeakValueDictionary
plugincontextdict = WeakValueDictionary()
socketcontextdict = WeakValueDictionary()
pluginnamedict = WeakKeyDictionary()
socketnamedict = WeakKeyDictionary()

_plugids = WeakKeyDictionary()

def report(*args):
  #print(*args)
  pass

def matchreport(*args):
  #print(*args)  
  #print("SOCKET", args[0].contextname, args[1],file=matchf)
  #print("PLUGIN", args[2].contextname, args[3],file=matchf)
  pass

def matchreport0(*args):
  #print(*args,file=matchf)
  pass

def namesortfunc(name):
  if isinstance(name, tuple):
    strings = ()
    numbers = ()
    for r in name:
      n,s = namesortfunc(r)
      numbers += n
      strings += s
    ret = (numbers, strings)
  else:
    name = encode_context(name)
    if isinstance(name,str): name = (name,)
    ret = ((len(name),), name)
  #if len(ret[0]) == 1 and ret[1] == ("evexc",): 
  #  return (maxtup, ("evexc",))
  return ret

def namesortfunc_match(name):
  if isinstance(name, tuple):
    strings = ()
    numbers = ()
    for r in name:
      n,s = namesortfunc_match(r)
      numbers += n
      strings += s
    ret = (numbers, strings)
  else:
    name = encode_context(name)
    if isinstance(name,str): name = (name,)
    if name[-1].startswith("<<"):
      nn = name[-1].split("-")
      if len(nn) == 2:
        name = name[:-1] + (nn[0], "%05d" % int(nn[1]))
      else:
        name = name + ("00000",)
    ret = ((-len(name),), name)
  #if len(ret[0]) == 1 and ret[1] == ("evexc",): 
  #  return (maxtup, ("evexc",))
  return ret

def bee_or_evexc(nam):
  if not isinstance(nam, tuple): return False
  if not len(nam): return False
  if nam == ("bee","init"): return False
  return nam[0] in ("bee", "evexc")

def find_subcontexts(context):
  from . import _contexts as contexts, get_curr_contextname, _all_connections
  currcontextname = encode_context(context.contextname)
  subcontextnames = [k for k in contexts.keys() if len(k) > len(currcontextname) and k[:len(currcontextname)] == currcontextname]
  subcontextnames.sort(key = namesortfunc)  
  subcontexts = []
  for subcontextname in subcontextnames: 
    for n in range(len(currcontextname)+1, len(subcontextname)):
      if subcontextname[:n] in contexts: break
    else:
      subcontexts.append(contexts[subcontextname])
  return subcontexts
 
def retrieve_plugins(context, plugin, visited=[]):
  try:
    return context.retrieved_plugins[plugin]
  except KeyError:
    pass

  ret = None
  if plugin in context.plugins: 
    ret = [(context.contextname, p) for p in context.plugins[plugin]]
  for contextinstance, name, newname, optional in context.plugin_imports:
    if contextinstance in visited: continue
    #report(name,newname, plugin)
    if newname == plugin: 
      if ret is None: ret = []
      newvisited = list(visited)
      newvisited.append(context)           
      #report("TRY!", contextinstance.contextname, name)
      ret2 = retrieve_plugins(contextinstance, name, newvisited)
      if ret2 != None: ret += ret2
  context.retrieved_plugins[plugin] = ret
  return ret

def retrieve_sockets(context, socket, visited=[]):
  try:
    return context.retrieved_sockets[socket]
  except KeyError:
    pass

  ret = None
  if socket in context.sockets: 
    ret = [(context.contextname, s) for s in context.sockets[socket]]
  for contextinstance, name, newname, optional in context.socket_imports:
    if contextinstance in visited: continue       
    if newname == socket: 
      if ret is None: ret = []
      newvisited = list(visited)
      newvisited.append(context)  
      ret2 = retrieve_sockets(contextinstance, name, newvisited)      
      if ret2 != None: ret += ret2
  context.retrieved_sockets[socket] = ret
  return ret
  
import traceback
from .plugin_base import plugin_base
from .socket_base import socket_base

#at runtime, you can get the context name of a socket or plugin: 
#x.im_self.workerinstance._context.contextname
#
#you can retrieve all targets from a push outputpin socket as:
#x.function.im_self.outputs
  
def namesortfunc2(c):
  name = c[0]
  name = encode_context(name)
  if isinstance(name,str): name = (name,)
  return (len(name), name)


def flatten(k):
  ret = []
  for i in k:
    if isinstance(i, str): ret.append(i)
    elif isinstance(i, tuple): ret += flatten(i)
    else: raise TypeError(i)
  return ret

def decode_context(contextargs):
  try:
    len(contextargs)
  except TypeError:
    raise TypeError("Context '%s' must be string or tuple, not %s" % (contextargs, contextargs.__class__.__name__))
  if len(contextargs) == 0: 
    raise TypeError("Context must have an identifier")
  ret = contextargs
  if len(contextargs) == 1:
    if hasattr(contextargs[0], "decode") or hasattr(contextargs[0], "encode"): ret = contextargs[0]
  for s in ret:
    if not hasattr(s, "decode") and not hasattr(s, "encode"): raise TypeError("Invalid context %s" % str(contextargs))
  return ret

def encode_context(contextargs):
  if hasattr(contextargs, "decode") or hasattr(contextargs, "encode"): 
    contextargs = (contextargs,)
  return contextargs

from .contextmatch import contextmatch
from .matchmake import matchmake

class context(object):
  import_all_from_parent = False
  import_parent_sockets = []
  import_parent_plugins = []
  import_parent_sockets_optional = []
  import_parent_plugins_optional = []  
  import_parent_skip = []
  parent_exported = False
  priority = 0
  connection = None
  subcontext = None
  def __init__(self,*contextargs,**kwargs):
    absolute = False
    if "absolute" in kwargs: absolute = kwargs["absolute"]
    from . import abscontextname, register_context
    self.contextname = decode_context(contextargs)
    if not absolute: self.contextname = abscontextname(self.contextname)    
    self.sockets = {}
    self.plugins = {}
    self.socket_imports = []
    self.plugin_imports = []
    register_context(self.contextname, self)
    self.preclose_functions = []
    self.postclose_functions = []
    self.closed = False    

    self.retrieved_plugins = {}
    self.retrieved_sockets = {}    
    
    self._postinit()
  def _postinit(self):
    pass
  def __overwriting__(self, oldcontextinstance):    
    raise Exception("Cannot register context %s: context already exists" % str(self.contextname))
  def __overwritten__(self, newcontextinstance):
    pass
  def context(self, contextname, contextinstance):
    contextname = decode_context(contextname)
    register_context(self.contextname + contextname, contextinstance)

  def parent_export(self):   
   report("PARENT-EXPORT", self.contextname)
   if self.parent_exported: return   
   subcontexts = find_subcontexts(self)
   for s in subcontexts: s.parent_export()
   self.parent_exported = True
   self.parent_do_export()

  
  def parent_import(self):   
   report("PARENT-IMPORT", self.contextname)
   self.parent_do_import()   
   subcontexts = find_subcontexts(self)
   for s in subcontexts: s.parent_import()
  
   
  def parent_do_export(self):
    report("PARENT-DO-EXPORT", self.contextname)  
    from . import _contexts as contexts, get_curr_contextname, _all_connections
    if not self.import_all_from_parent: return   
    #report("PARENT-EXPORT", self.contextname)
    #report(self.plugins.keys(), [p[2] for p in self.plugin_imports])
    #report(self.sockets.keys(), [p[2] for p in self.socket_imports])
    #report("")

    parent = None
    myname = self.contextname        
    while True:
      myname = myname[:-1]
      if not len(myname): break
      if myname in contexts:
        parent = contexts[myname]
        break

    if parent is None: return

    for sock in sorted(self.sockets,key=namesortfunc):
      if bee_or_evexc(sock): 
        continue
      parent.import_socket(self, sock)
    for plug in sorted(self.plugins,key=namesortfunc):
      if bee_or_evexc(plug): 
        continue
      parent.import_plugin(self, plug)

    for sock in self.socket_imports:
      if sock[0] is parent: continue
      if sock in parent.socket_imports: continue
      if bee_or_evexc(sock[2]): continue
      report("SOCK-IMPORT-APPEND", self.contextname, sock[1], sock[2])
      parent.socket_imports.append(sock)

    for plug in self.plugin_imports:
      if plug[0] is parent: continue
      if plug in parent.plugin_imports: continue
      if bee_or_evexc(plug[2]): continue
      report("PLUG-IMPORT-APPEND", self.contextname, plug[1], plug[2])
      parent.plugin_imports.append(plug)
      
  def parent_do_import(self):
    report("PARENT-DO-IMPORT", self.contextname)
    from . import _contexts as contexts, get_curr_contextname, _all_connections
    if not self.import_all_from_parent: return   

    parent = None
    myname = self.contextname        
    while True:
      myname = myname[:-1]
      if not len(myname): break
      if myname in contexts:
        parent = contexts[myname]
        break
    if parent is None: return

    parent2 = parent
    parent_old = parent

    #report("PARENT-IMPORT", self.contextname, parent_old.contextname)
    #report(list(parent.plugins.keys()), [p[2] for p in parent.plugin_imports])
    #report(list(parent.sockets.keys()), [p[2] for p in parent.socket_imports])
    #report("")

    for sock in sorted(parent.sockets,key=namesortfunc):
      if bee_or_evexc(sock):
        continue
      self.import_socket(parent2, sock)
    for plug in sorted(parent.plugins,key=namesortfunc):
      if bee_or_evexc(plug): 
        continue
      self.import_plugin(parent2, plug)

    for sock in parent.socket_imports:
      if sock[0] is self: continue
      if sock in self.socket_imports: continue
      if bee_or_evexc(sock[2]): continue      
      report("SOCK-IMPORT-APPEND2", self.contextname, sock[1], sock[2])
      self.socket_imports.append(sock)

    for plug in parent.plugin_imports:
      if plug[0] is self: continue
      if plug in self.plugin_imports: continue
      if bee_or_evexc(plug[2]): continue      
      report("PLUG-IMPORT-APPEND2", self.contextname, plug[1], plug[2])
      self.plugin_imports.append(plug)

  def do_connect(self):
    report("CONNECT", self.contextname)
    from . import _contexts as contexts, get_curr_contextname, _all_connections
    if not self.connection: return   
    #report("CONNECT", self.contextname)
    #report(self.plugins.keys(), [p[2] for p in self.plugin_imports])
    #report(self.sockets.keys(), [p[2] for p in self.socket_imports])
    #report("")

    parent = self.connection   
    for sock in sorted(parent.sockets,key=namesortfunc):
      if bee_or_evexc(sock): 
        continue
      self.import_socket(parent, sock)
    for plug in sorted(parent.plugins,key=namesortfunc):
      if bee_or_evexc(plug): 
        continue
      self.import_plugin(parent, plug)

    for sock in parent.socket_imports:
      if sock[0] is self: continue
      nam = sock[2]
      if bee_or_evexc(nam): 
        continue      
      report("SOCK-IMPORT-APPEND3", self.contextname, sock[1], sock[2])
      self.socket_imports.append(sock)

    for plug in parent.plugin_imports:
      if plug[0] is self: continue
      nam = plug[2]
      if bee_or_evexc(nam): 
        continue      
      report("PLUG-IMPORT-APPEND3", self.contextname, plug[1], plug[2])
      self.plugin_imports.append(plug)
   
  def close(self):
    if self.closed: return
    if self.subcontext != None: self.subcontext.__close__()     
    from . import _contexts as contexts, get_curr_contextname

    for f in self.preclose_functions:
      f()     

    myname = self.contextname     
    """
    parent = None
    while True:
      myname = myname[:-1]
      if not len(myname): break
      if myname in contexts:
        parent = contexts[myname]
        break
    if parent:
      for s in self.import_parent_sockets:
        if retrieve_sockets(parent, s) is None:
          raise Exception("Context %s has required socket import %s from parent, but parent doesn't have that socket" % (myname, s))     
      for p in self.import_parent_plugins:
        if retrieve_plugins(parent, p) is None:
          raise Exception("Context %s has required plugin import %s from parent, but parent doesn't have that plugin" % (myname, p))
      if self.import_all_from_parent:   
        socks, plugs = [],[]
        #print "CLOSE-FRAME", self.contextname
        def match(h1,h2):
          if isinstance(h1, str): h1 = (h1,)
          if isinstance(h2, str): h2 = (h2,)
          if len(h1) > len(h2):return False
          for hh1, hh2 in zip(h1,h2):
            if hh1 != hh2: return False
          return True
        def skipfilter(l):
          ret = []
          for x in l:
            for sk in self.import_parent_skip:
              if match(sk, x):
                break
            else: ret.append(x)
          return ret

        newsocks = []
        for x in parent.socket_imports:
          xx = x[2]
          if bee_or_evexc(xx): continue
          if xx in newsocks: continue
          report("NEWSOCK", self.contextname, xx)
          newsocks.append(xx)

        newplugs = []
        for x in parent.plugin_imports:
          xx = x[2]
          if bee_or_evexc(xx): continue            
          if xx in newplugs: continue
          report("NEWPLUG", self.contextname, xx)
          newplugs.append(xx)

        socks0 = sorted(list(parent.sockets.keys()),key=namesortfunc)
        socks0 = [s for s in socks0 if not bee_or_evexc(s)]
        socks = skipfilter(socks0 + newsocks)
        plugs0 = sorted(list(parent.plugins.keys()),key=namesortfunc)
        plugs0 = [p for p in plugs0 if not bee_or_evexc(p)]
        plugs = skipfilter(plugs0 + newplugs)
      else:        
        if len(self.import_parent_sockets + self.import_parent_plugins):
          raise Exception("Context %s has required imports from parent, but doesn't have a parent" % myname)        
        socks = self.import_parent_sockets + self.import_parent_sockets_optional
        plugs = self.import_parent_plugins + self.import_parent_plugins_optional
      for s in socks:
        self.import_socket(parent, s, optional=True)
      for p in plugs:
        self.import_plugin(parent, p, optional=True)
    """
    selfcontextname = encode_context(self.contextname)
    subcontextnames0 = [k for k in contexts.keys() if len(k) > len(selfcontextname) and k[:len(selfcontextname)] == selfcontextname]
    subcontextnames0.sort(key = namesortfunc_match)  

    subcontextnames = []
    subcontexts = []
    for subcontextname in subcontextnames0: 
      if subcontextname[-1].startswith("<<") or subcontextname[-1] == "evexc": continue
      subnames0 = [subcontextname]
      for s in subcontextnames0:
        if not s[-1].startswith("<<") and s[-1] != "evexc": continue
        if s[:-1] == subcontextname: subnames0.append(s)
        elif s[-1] == "evexc" and s[:-2] == subcontextname: subnames0.append(s)
      subs = [contexts[s] for s in subnames0]
      subs.sort(key = lambda s:-s.priority)
      subcontexts += subs
      subnames = [sub.contextname for sub in subs]
      subcontextnames += subnames

    subnames0 = []
    for k in contexts.keys():
      if k in subcontextnames: continue
      if k[:len(selfcontextname)] == selfcontextname: subnames0.append(k)
    subs = [contexts[s] for s in subnames0]
    subs.sort(key = lambda s:-s.priority)
    subcontexts += subs
    subnames = [sub.contextname for sub in subs]
    subcontextnames += subnames            
    
    #if len(subcontextnames):
    #  for c in subcontextnames: print(c)
    matchmake(self, subcontexts, subcontextnames)
    
    """
    contextmatch (
      self, self.contextname, 
      self.sockets, self.plugins,
      self.socket_imports, self.plugin_imports,
      self.socket, self.plugin
    )
    """
    
    for f in self.postclose_functions:
      f()
    self._postclose()
    if get_curr_contextname() == self.contextname: pop()
    self.closed = True
      
  def socket(self, keyword, socketinstance):
    assert isinstance(socketinstance, socket_base) or socketinstance == None
    ret = False
    if keyword not in self.sockets: self.sockets[keyword] = []
    if socketinstance not in self.sockets[keyword]:
      self.sockets[keyword].append(socketinstance)    
      ret = True
    if socketinstance not in socketcontextdict:  
      socketcontextdict[socketinstance] = self
      socketnamedict[socketinstance] = keyword
    return ret  
  def plugin(self, keyword, pluginstance):
    assert isinstance(pluginstance, plugin_base) or pluginstance == None
    ret = False
    if keyword not in self.plugins: self.plugins[keyword] = []
    if pluginstance not in self.plugins[keyword]:
      if pluginstance not in _plugids:
        _plugids[pluginstance] = len(list(_plugids.values()))
      self.plugins[keyword].append(pluginstance)
      ret = True
    if pluginstance not in plugincontextdict:  
      plugincontextdict[pluginstance] = self    
      pluginnamedict[pluginstance] = keyword
    return ret  
  def preclose(self, preclose_function):
    self.preclose_functions.append(preclose_function)    
  def postclose(self, postclose_function):
    self.postclose_functions.append(postclose_function)
  def _postclose(self):
    pass
  
  def import_socket(self, contextinstance, name, newname = None, optional = False):  
    assert isinstance(contextinstance, context)
    assert contextinstance is not self
    ret = False
    if newname == None: newname = name
    n = (contextinstance, name, newname, optional)
    if n not in self.socket_imports:    
      self.socket_imports.append(n)    
      ret = True
    try:
      r = self.retrieved_sockets[newname]
      if r is None: r = []
      for c in contextinstance.retrieved_sockets[name]:
        if c not in r: r.append(c)
      if r: self.retrieved_sockets[newname] = r
    except KeyError:
      pass
    return ret  
  def import_plugin(self, contextinstance, name, newname = None, optional = False):  
    assert isinstance(contextinstance, context)
    assert contextinstance is not self
    ret = False
    if newname == None: newname = name
    n = (contextinstance, name, newname, optional)
    if n not in self.plugin_imports:
      self.plugin_imports.append(n)    
      ret = True
    try:
      r = self.retrieved_plugins[newname]
      if r is None: r = []
      for c in contextinstance.retrieved_plugins[name]:
        if c not in r: r.append(c)
      if r: self.retrieved_plugins[newname] = r
    except KeyError:
      pass
    return ret  
      
  def export_socket(self, contextinstance, name, newname = None, optional = False):  
    assert isinstance(contextinstance, context)
    assert contextinstance is not self
    if newname == None: newname = name
    contextinstance.socket_imports.append((self, name, newname, optional))    
  def export_plugin(self, contextinstance, name, newname = None, optional = False):  
    assert isinstance(contextinstance, context)
    assert contextinstance is not self
    if newname == None: newname = name
    contextinstance.plugin_imports.append((self, name, newname, optional))    
  
class connect:
  def __init__(self, socket, plugin):
    socketcontextname, socketname = socket
    plugincontextname, pluginname = plugin
    from . import add_contextnames, _contexts, get_curr_contextname
    socketcontextname = add_contextnames(get_curr_contextname(), socketcontextname)
    assert socketcontextname in _contexts, socketcontextname
    self.socketcontext = _contexts[socketcontextname]
    assert socketname in self.socketcontext.sockets
    self.socketname = socketname

    plugincontextname = add_contextnames(get_curr_contextname(), plugincontextname)    
    assert plugincontextname in _contexts, plugincontextname
    self.plugincontext = _contexts[plugincontextname]    
    assert pluginname in self.plugincontext.plugins    
    self.pluginname = pluginname

  def place(self):
    from . import new_abscontextname, add_contextnames
    newplugincontextname = new_abscontextname(add_contextnames(self.plugincontext.contextname, "<<connect"))
    newplugincontext = context(*newplugincontextname,absolute=True)
    
    newplugincontext.import_socket(self.socketcontext, self.socketname, self.pluginname)
    newplugincontext.import_plugin(self.plugincontext, self.pluginname)
    
    newsocketcontextname = new_abscontextname(add_contextnames(self.socketcontext.contextname, "<<connect"))
    newsocketcontext = context(*newsocketcontextname,absolute=True)
    
    newsocketcontext.import_socket(self.socketcontext, self.socketname)
    newsocketcontext.import_plugin(self.plugincontext, self.pluginname, self.socketname)
    return newplugincontext, newsocketcontext
    
    
class subcontext(object):
  def __init__(self, contextname, hive, import_parent_sockets = [], 
                                       import_parent_plugins = [], 
                                       import_parent_sockets_optional = [], 
                                       import_parent_plugins_optional = [],
                                       import_parent_skip = []):
    assert hive in (True, False)    
    self._contextname = decode_context(contextname)
    self._hive = hive
    self._make_context = False
    self._import_parent_sockets = import_parent_sockets
    self._import_parent_plugins = import_parent_plugins
    self._import_parent_sockets_optional = import_parent_sockets_optional
    self._import_parent_plugins_optional = import_parent_plugins_optional    
    self._import_parent_skip = import_parent_skip    
  def __place__(self):
    pass
  def make_context(self):
    from . import new_contextname  
    if not self._make_context:
      self._contextname = new_contextname(self._contextname)
      self.context = context(self._contextname)
      self.context.subcontext = self
      if not self._hive:
        self.context.import_all_from_parent = True
        assert not len(self._import_parent_sockets_optional), self._import_parent_sockets_optional
        assert not len(self._import_parent_plugins_optional), self._import_parent_plugins_optional
      self.context.import_parent_sockets = self._import_parent_sockets
      self.context.import_parent_plugins = self._import_parent_plugins
      self.context.import_parent_sockets_optional = self._import_parent_sockets_optional
      self.context.import_parent_plugins_optional = self._import_parent_plugins_optional 
      self.context.import_parent_skip = self._import_parent_skip
      self._make_context = True
  def place(self):
    from . import push, pop
    self.make_context()
    try:
      push(self._contextname)
      self.__place__()
    finally:
      pop()
  def __close__(self):
    pass
  def close(self):
    self.context.close()
    
