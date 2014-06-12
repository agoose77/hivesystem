from .segments._helpersegment import reg_helpersegment

class reg_beehelper(reg_helpersegment):
  def __new__(metacls, name, bases, dic, **kargs):
    if "__reg_enabled__" not in dic:
      for b in bases:
        d = b.__dict__
        if "__reg_enabled__" in d: 
          dic["__reg_enabled__"] = d["__reg_enabled__"]
    return reg_helpersegment.__new__(metacls, name, bases, dic, **kargs)

from . import myobject
class beehelper(myobject):
  __metaclass__ = reg_beehelper


class tupledummy(tuple):
  def __getattr__(self, attr):   
    if attr.startswith("_"): raise AttributeError
    ret = self + tupledummy((attr,))
    return ret

class beewrapper(beehelper):
  _wrapped_hive = None
  def __init__(self, *args, **kargs):
    self.args = args
    self.args2 = tuple(args)
    self.kargs = kargs
    self.kargs2 = kargs.copy()
    self.instance = None
  def getinstance(self,__parent__ = None):
    from .drone import dronebuilder
    from .worker import worker, workerframe
    
    if issubclass(self._wrapped_hive.__class__,dronebuilder) or \
     issubclass(self._wrapped_hive, workerframe) or \
     "__parent__" in self.kargs2: #drone or worker or __parent__ in kargs2
      self.instance = self._wrapped_hive(*self.args2, **self.kargs2)
    else:
      self.instance = self._wrapped_hive(*self.args2, __parent__=__parent__, **self.kargs2)
    self.instance._hive_parameters = self.kargs2
    return self.instance  
  def set_parameters(self, name, parameters):
    from .parameter import parameter as bee_parameter
    from .resolve import resolve
    args2_new = []
    for pnr, p in enumerate(self.args):
      if isinstance(p, bee_parameter):
        raise TypeError("'%s', argument %d: Cannot retrieve value from bee.parameter, use bee.get_parameter instead" % (name, pnr+1))
      args2_new.append(resolve(p,parameters=parameters,prebuild=True))      
    self.args2 = args2_new  
    for k in self.kargs:
      p = self.kargs[k]      
      if isinstance(p, bee_parameter):        
        raise TypeError("'%s', argument '%s': Cannot retrieve value from bee.parameter, use bee.get_parameter instead" % (name,k))
      self.kargs2[k]  = resolve(p,parameters=parameters,prebuild=True)
    
  def __getattr__(self, attr):
    try:      
      if self.instance != None:
        ret = getattr(self.instance, attr)
      else:
        ret = getattr(self._wrapped_hive, attr)
    except AttributeError:  
      if attr == "__nested_tuple__": raise
      if hasattr(self, "__nested_tuple__") and self.__nested_tuple__ == True: 
        ret = tupledummy((self, attr))
      else:
        ret = (self, attr)
    return ret


