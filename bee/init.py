import libcontext, functools, traceback, sys
from .resolve import resolve
from .beewrapper import beewrapper
from .configure import configure_base, delayedcall

class InitBeeException(Exception): pass
    
class init(configure_base):
  def __init__(self, target):
    self.target_original = target
    self.initialization = []
  
    self.target = target
    self.bound_target = True
          
    if isinstance(target, str):
      self.target = target
    elif hasattr(target, "__get_beename__"):
      self.target = target
      self.bound_target = False
    else: raise TypeError(target)
    
  def bind(self):
    if not self.bound_target:
      if isinstance(self.target.__get_beename__, tuple): raise TypeError(self.target)
      self.target = self.target.__get_beename__(self.target)
      self.bound_target = True      

  def hive_init(self, beedict):
    if not self.bound_target:
      from .drone import drone
      if isinstance(self.target.instance, drone) \
       and self.target.instance in beedict.values():
        self.target = [v for v in beedict if beedict[v] is self.target.instance][0]          
      else:        
        self.bind()
    n = beedict[self.target]
    n = resolve(n,parameters=self.parameters)
    if n is self: raise Exception("bee.init target '%s' is self" % self.target)    
    from .worker import workerframe
    if isinstance(n, beewrapper):
      assert n.instance is not None
      n = n.instance       
    if isinstance(n, workerframe):
      assert n.built  
      n = n.bee 
    for attrs, stack, args, kargs in self.initialization:
      args = tuple([resolve(a,parameters=self.parameters) for a in args])
      kargs = dict((a,resolve(kargs[a],parameters=self.parameters)) for a in kargs)      
      try:
        nn = n  
        setitem = False     
        for mode, attr in attrs:
          if mode == "getattr":
            nn = getattr(nn, attr)
          elif mode == "getitem":
            nn = nn[attr]
          elif mode == "setitem":
            attr, value = attr
            nn[attr] = value
            setitem = True
          else: raise Exception(mode) #should never happen            
        if not setitem:  
          nn(*args, **kargs)
      except Exception as e:
        s1 = traceback.format_list(stack[:-1])
        tbstack = traceback.extract_tb(sys.exc_info()[2])
        s2 = traceback.format_list(tbstack[1:])
        s3 = traceback.format_exception_only(type(e),e)
        s = "\n"+"".join(s1 + s2 + s3)
        raise InitBeeException(s)
    if isinstance(n, configure_base): n.hive_init(beedict)
    
  def __init_append__(self, attr, stack, *args, **kargs):
    self.initialization.append((attr, stack, args, kargs))
    return self

  def __getattr__(self, attr):
    if attr == "typename": raise AttributeError
    stack = traceback.extract_stack()  
    return delayedcall(self,self.__init_append__, [("getattr",attr)], stack)
  def __getitem__(self, attr):
    stack = traceback.extract_stack()  
    return delayedcall(self,self.__init_append__, [("getitem",attr)], stack)
  def __setitem__(self, attr, value):
    stack = traceback.extract_stack()  
    at = [("setitem", (attr, value))]
    self.initialization.append((at, stack, [], {}))

  def set_parameters(self,name,parameters):
    self.parameters = parameters
    
