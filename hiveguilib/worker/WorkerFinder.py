from __future__ import print_function, absolute_import

import sys, os
import spyder, Spyder
import bee

class FindWorkerState(object):
  def __init__(self):
    self.workers = {}
    self.metaworkers = {}
    self.hivemapworkers = {}
    self.spydermapworkers = {}
    self.drones = {}
    self.spyderhives = {}
    self.suspect = []
  def update(self, other):
    assert isinstance(other, FindWorkerState)
    self.workers.update(other.workers)
    self.metaworkers.update(other.metaworkers)
    self.hivemapworkers.update(other.hivemapworkers)
    self.spydermapworkers.update(other.spydermapworkers)
    self.drones.update(other.drones)
    self.spyderhives.update(other.spyderhives)
    self.suspect += other.suspect
  
def add_worker(worker, workername, findworkerstate, found_workers):
  w = worker
  try:
    if hasattr(w, "guiparams") and ("antennas" in w.guiparams or "outputs" in w.guiparams):            
      #worker, worker-like hive, or shim object (e.g. WorkerGUI segments)
      findworkerstate.workers[workername] = w
      found_workers.add(id(w))
      return True
    elif hasattr(w, "metaguiparams"):        
      findworkerstate.metaworkers[workername] = w
      found_workers.add(id(w))
      return True
    elif hasattr(w, "__hivebases__"):
      if bee.frame in w.__hivebases__ or bee.frame in w.__allhivebases__: #drone-like hive, treated as worker
        findworkerstate.workers[workername] = w
        found_workers.add(id(w))
        return True
      elif bee.spyderhive.spyderframe in w.__hivebases__ \
       or bee.spyderhive.spyderdicthive in w.__hivebases__ \
       or bee.spyderhive.spyderhivecontext in w.__allhivebases__ \
       or bee.spyderhive.spyderdicthivecontext in w.__allhivebases__ \
       or bee.combohive in w.__hivebases__ : #spyderhive
        findworkerstate.spyderhives[workername] = w
        found_workers.add(id(w))
        return True
    elif hasattr(w, "_wrapped_hive"): #true drones
      if issubclass(w._wrapped_hive, bee.drone):
        findworkerstate.drones[workername] = w
        found_workers.add(id(w))
    elif hasattr(w, "__drone__"): #drone-like shim object
      findworkerstate.drones[workername] = w
      found_workers.add(id(w))    
  except TypeError:
    pass
  return False

def find_workers(mod, modname, done_mods, found_workers, star = False, search_path=True, lister = None, opener = None):    
  if modname.endswith("__init__"): raise Exception  
  if id(mod) in done_mods: return {},{}
  import glob,os,imp, functools
  if lister is None: lister = os.listdir
  if opener is None: opener = functools.partial(open, mode="r")
  findworkerstate = FindWorkerState()
  done_mods.add(id(mod))
  modname2 = modname.rstrip(".__init__")
  for v in dir(mod):
    if v in ("frame","hive","closedhive","inithive","raiser"): continue
    if isinstance(v, os.__class__): #is a module...
      newmodname = modname+"."+v
      newfindworkerstate = \
       find_workers(v, newmodname, done_mods, found_workers, lister=lister, opener=opener)
      findworkerstate.update(newfindworkerstate)
      continue
    vv = getattr(mod, v)
    if id(vv) in found_workers: continue
    workername = modname+"."+v
    if hasattr(vv, "__module__") and vv.__module__ is not None: 
      if not vv.__module__.startswith(modname2):
        if hasattr(vv, "guiparams") or hasattr(vv, "metaguiparams"):
          if not vv.__module__.startswith("bee.segments"):
            findworkerstate.suspect.append((workername, v, vv))
        continue
    add_worker(vv, workername, findworkerstate, found_workers)

  p = mod.__file__
  motif = ""
  if p.startswith("//"):
    p = p[2:]
    motif = "//"
  path = motif + os.path.split(p)[0]
  newmodules = []
  newstarmodules = []
  if search_path:
    for f in lister(path):
      ff = path + os.sep + f
      if (ff.endswith(".web") or ff.endswith(".hivemap") or ff.endswith(".spydermap")):
        try:
          spydertype, spyderdata = spyder.core.parse(opener(ff).read())
        except:
          import traceback
          traceback.print_exc()
          continue
        if ff.endswith(".web") or ff.endswith(".hivemap"):
          if spydertype == "Hivemap": 
            try:
              hivemap = Spyder.Hivemap(spyderdata)
            except:
              print("Error in importing '%s':" % ff)
              import traceback
              traceback.print_exc()
              continue
            newhivemapname = modname + ":" + f
            findworkerstate.hivemapworkers[newhivemapname] = hivemap
        if ff.endswith(".web") or ff.endswith(".spydermap"):
          if spydertype == "Spydermap": 
            try:
              #spydermap = Spyder.Spydermap(spyderdata)
              spydermap = Spyder.Spydermap.fromfile(ff)
            except:
              print("Error in importing '%s':" % ff)
              import traceback
              traceback.print_exc()
              continue
            newspydermapname = modname + "#" + f
            findworkerstate.spydermapworkers[newspydermapname] = spydermap

      elif star:
        if ff.endswith(".py"):
          n = f[:-len(".py")]
          newstarmodules.append((n,ff))
        elif ff.endswith(".spy"):
          #n = f[:-len(".spy")]
          #newstarmodules.append((n,ff))
          pass #importing like this is not a good idea...
      else:
        if os.path.isdir(ff) and os.path.exists(ff+os.sep+"__init__.py"): newmodules.append(f)
  for n in newmodules:
    newmodname = modname + "." + n
    if newmodname in findworkerstate.workers or \
     newmodname in findworkerstate.metaworkers: continue
    
    try:
      if newmodname not in sys.modules:
        __import__(newmodname)
    except ImportError:    
      print("Error in importing", newmodname)
      import traceback
      traceback.print_exc()
      continue
    newmod = sys.modules[newmodname]
    search_path = newmod.__file__.endswith("__init__.pyc") or mod.__file__.endswith("__init__.py")
    newfindworkerstate = \
     find_workers(newmod, newmodname, done_mods, found_workers,
      search_path=search_path,
      lister=lister, opener=opener
     )
    findworkerstate.update(newfindworkerstate)
  for n,ff in newstarmodules:
    if n == "__init__": continue
    newmodname = modname + "." + n
    if newmodname in findworkerstate.workers or \
     newmodname in findworkerstate.metaworkers: continue
    try:
      if newmodname not in sys.modules:
        if ff.endswith(".spy"):
          #__import__(newmodname)        
          raise Exception ##importing like this is not a good idea...
        elif opener is not None:
          __import__(newmodname)
          sys.modules[newmodname].__file__ = ff
        else:
          fil = open(ff, "r")
          imp.load_module(newmodname,fil,ff,("py","r",imp.PY_SOURCE ))
    except ImportError:    
      print("Error in importing", newmodname)
      import traceback
      traceback.print_exc()
      continue
    newmod = sys.modules[newmodname]
    search_path = newmod.__file__.endswith("__init__.pyc") or mod.__file__.endswith("__init__.py")
    newfindworkerstate = \
     find_workers (
      newmod, newmodname,done_mods,found_workers, 
      search_path=search_path,
      lister = lister,
      opener = opener,
    ) 
    findworkerstate.update(newfindworkerstate)
    
  return findworkerstate


class WorkerFinder(object):  
  @staticmethod
  def find_locationmodules(locationconfs, localdir=None, readlines = None):
    locationmodules = [] 
    
    syspath = []
    if localdir is not None: syspath = [localdir]
    syspath += list(sys.path)
    
    for lconf in locationconfs:
      if readlines is None:
        lines = open(lconf).readlines()
      else:
        lines = readlines(lconf)
      for l in lines:
        l = l.strip()
        if l.startswith("#"): continue
        if not len(l): continue
        if l.startswith("@"): 
          l = os.path.expandvars(l[1:])
          if localdir is not None:
            ll = localdir+os.sep+l
            if os.path.isdir(ll):
              syspath.append(ll)
            else: 
              syspath.append(l)              
          else: 
            syspath.append(l)
        else: 
          locationmodules.append(l)
    return locationmodules, syspath

  def __init__(self, locationmodules, syspath, found_workers = None, lister = None, opener = None):
    self.lister = lister
    self.opener = opener
    self._done_mods = set()
    self._found_workers = set()
    if found_workers is not None:
      for w in found_workers: 
        self._found_workers.add(w)

    findworkerstate = FindWorkerState()
    syspath_backup = list(sys.path)
    sys.path = syspath 
    for m in locationmodules:
      star = False
      if m.endswith(".*"):
        star = True
        m = m[:-2]
      try:
        if m not in sys.modules:
          __import__(m)
        mod = sys.modules[m]
        if mod.__file__.endswith(".spy"): continue
        search_path = mod.__file__.endswith("__init__.pyc") or mod.__file__.endswith("__init__.py")
        newfindworkerstate = \
         find_workers (
          mod, m, self._done_mods, self._found_workers, star, 
          search_path = search_path, 
          lister = self.lister,
          opener = self.opener,
        )
        findworkerstate.update(newfindworkerstate)
      except:
        print("Error in importing", m)
        import traceback
        traceback.print_exc()

    sys.path = syspath_backup
    
    for workername, varname, worker in findworkerstate.suspect:
      if id(worker) in self._found_workers: continue
      altworkername = worker.__module__ + "." + varname
      if altworkername in findworkerstate.workers or \
       altworkername in findworkerstate.metaworkers:
        continue
      add_worker(
       worker, workername, findworkerstate, self._found_workers
      )
          
    self.workers = findworkerstate.workers
    self.metaworkers = findworkerstate.metaworkers
    self.hivemapworkers = findworkerstate.hivemapworkers
    self.spydermapworkers = findworkerstate.spydermapworkers
    self.drones = findworkerstate.drones
    self.spyderhives = findworkerstate.spyderhives
    self.typelist = set()
    for w in self.workers.values():      
      gp = w.guiparams
      wtypes = list(gp.get("antennas",{}).values()) + \
       list(gp.get("outputs",{}).values())
      for t in wtypes: 
        self.typelist.add(t[1])            
      