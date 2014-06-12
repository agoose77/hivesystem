from .beewrapper import beewrapper, reg_beehelper

from . import emptyclass, mytype

class dronebuilder(reg_beehelper):
  __droneclassname__ = "Drone"
  __reqdronefunc__ = "place"
  def __init__(self, name, bases, dic, *args, **kargs):
    mytype.__init__(self,name,bases,dic)
  def __new__(metacls, name, bases, dic, **kargs):
    if emptyclass in bases: 
      #print("emptyclass", name)
      bases = tuple([b for b in bases if b != emptyclass])      
      return type.__new__(metacls, name, bases, dict(dic))  

    bases0 = bases
    bases = []
    extrabases = []
    for b in bases0:
      if hasattr(b, "_wrapped_hive") and not isinstance(b._wrapped_hive, tuple):
        bases.append(b._wrapped_hive)
        extrabases.append(b._wrapped_hive)
        extrabases += b._wrapped_hive.__mro__[1:]
      else: 
        bases.append(b)        
        extrabases.append(b)
    bases = tuple(bases)
    
    if metacls.__reqdronefunc__ not in dic:
      ok = False
      for b in extrabases:
        if hasattr(b, metacls.__reqdronefunc__):
          at = getattr(b, metacls.__reqdronefunc__)
          if not isinstance(at, tuple):
            ok = True
            break
      if ok == False:
        raise Exception("%s '%s' (or its base classes) must define a %s method" % (metacls.__droneclassname__, name, metacls.__reqdronefunc__))
    if "__beename__" not in dic: dic["__beename__"] = name
    if "guiparams" not in dic: 
      d = {}
      for b in extrabases:
        if hasattr(b, "guiparams"): d.update(b.guiparams)
      dic["guiparams"] = d
    dic["guiparams"]["__beename__"] = dic["__beename__"]
    edrone = type.__new__(metacls, name+"&", bases, dict(dic))
    return type.__new__(metacls, name, (beewrapper,), {"_wrapped_hive":edrone, "guiparams":dic["guiparams"], "__metaclass__":dronebuilder})
    
class drone(emptyclass):
  __metaclass__=dronebuilder
  
class combodronebuilder(dronebuilder):
  __droneclassname__ = "Combo drone"
  __reqdronefunc__ = "make_combo"
  
class combodrone(emptyclass):
  __metaclass__=combodronebuilder 
  
def combodronewrapper(*args,**kwargs):
  for k in kwargs:
    if k not in ("combolist", "combodict"):
      raise TypeError("Unknown keyword argument '%s'" %  k)
  combolist, combodict = None, None
  if "combolist" in kwargs: combolist = kwargs["combolist"]
  if "combodict" in kwargs: combodict = kwargs["combodict"]
  
  count = len(args) + (combolist != None) + (combodict != None)
  if count < 1: raise TypeError("Too few arguments for combodronewrapper")
  if count > 2: raise TypeError("Too many arguments for combodronewrapper")
  clist, cdict = [],{}
  exc1 = TypeError("Combolist must be list instance")
  exc2 = TypeError("Combodict must be dict instance")  
  exc3 = TypeError("First argument must be list instance")  
  exc4 = TypeError("First argument must be dict instance")  
  exc5 = TypeError("First argument must be list or dict instance")  
  exc6 = TypeError("Second argument must be list or dict instance")    
  exc7 = TypeError("First and second arguments must be list and dict instances")
  if len(args) == 0:
    if combolist != None: 
      if not isinstance(combolist, list): raise exc1
      clist = combolist
    if combodict != None: 
      if not isinstance(combodict, dict): raise exc2
      cdict = combodict
  elif len(args) == 1:
    if combolist != None:
      if not isinstance(combolist, list): raise exc1
      clist = combolist
      if not isinstance(args[0], dict): raise exc4
      cdict = args[0]
    elif combodict != None:
      if not isinstance(combodict, dict): raise exc2
      cdict = combodict
      if not isinstance(args[0], list): raise exc3
      clist = args[0]    
    else:
      if not isinstance(args[0], list) and not isinstance(args[0],dict): raise exc5
      if isinstance(args[0], list): clist = args[0]
      else: cdict = args[0]
  else: #len(args) == 2
    l1, d1 = isinstance(args[0], list), isinstance(args[0],dict)
    l2, d2 = isinstance(args[1], list), isinstance(args[1],dict)    
    if not l1 and not d1: raise exc5
    if not l2 and not d2: raise exc6
    if l1 == l2: raise exc7

    if l1: clist = args[0]
    else: clist = args[1]

    if d1: cdict = args[0]
    else: cdict = args[1]
    
  class wrappedcombodrone(combodrone):
    def make_combo(self):
      return clist, cdict
  ret = wrappedcombodrone()

  
  from .hivemodule import allreg
  for item in clist+list(cdict.values()):
    if isinstance(item, list): it = item
    elif isinstance(item, dict): it = list(item.values())
    else: it = [item]
    for i in it:
      try:
        allreg.add(i)
      except TypeError:
        pass
  
  #Remove the combodrone from the current code frame and add it to the caller frame
  # as if it was initialized in the caller frame
  reg = ret.__metaclass__.reg
  import inspect
  fr = id(inspect.currentframe().f_back)  
  fr2 = id(inspect.currentframe().f_back.f_back)  
  if fr not in reg: reg[fr] = []
  if fr2 not in reg: reg[fr2] = []
  reg[fr].remove(ret)
  reg[fr2].append(ret)

  return ret
  
import libcontext
def dummydrone(plugindict={}, socketdict={}):
  class dummydrone(drone):
    def place(self):
      for pluginname, plugin in self.plugindict.items():
        libcontext.plugin(pluginname, plugin)
      for socketname, socket in self.socketdict.items():
        libcontext.socket(socketname, socket)
  ret = dummydrone()
  ret._wrapped_hive.plugindict = plugindict
  ret._wrapped_hive.socketdict = socketdict
  return ret
        
  

