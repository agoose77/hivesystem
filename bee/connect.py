from __future__ import print_function
import libcontext
from libcontext import context, evincontext, evoutcontext, evexccontext
from .hivemodule import beehelper, hivewrapper, evwrapper
from .types import typecompare

class proxy(object):
  def __init__(self, source, target):
    self.source = source
    self.target = target
  
class connectioncontext(context):
  priority = 2
  def parent_do_export(self):
    pass

def undollar(contextname):
  if isinstance(contextname, str):
    return contextname.lstrip("$")
  else:
    if len(contextname) == 0: return contextname
    last = contextname[-1].lstrip("$")
    return contextname[:-1] + (last,)
    
def search_beename(bee0, hive, io, nosub):
  from . import io as _io
  hivedict = dict(hive.beewrappers)
  ret = None
  beewraps = set([wname for wname,w in hive.beewrappers])
  subname = ()

  bee = bee0
  if isinstance(bee, tuple):
    bee, subname = bee[0], bee[1:]
  for wname, w in hive.beewrappers:
    found = False
    if w is bee:
      found = True
    elif isinstance(w, _io.antenna) or isinstance(w, _io.output):      
      inst = [b for beename,b in hive.bees if beename == wname][0]
      if inst.connector is bee:
        found = True        
    if found:
      if "@"+wname in beewraps: 
        if nosub == False:
          wname = "@"+wname
        else:
          wname = "$"+wname
      if io is None:
        if ret is not None:
          raise Exception("Duplicate bee %s" % wname)
        ret = (wname,)+subname, None
      else:
        if ret is not None:
          raise Exception("Duplicate bee %s" % wname)              
        ret = (wname,)+subname, io 
  for wname, w in hive.beewrappers:
    if not isinstance(w, hivewrapper): continue
    r = search_beename(bee0, w, io, nosub)
    if r[0] is not None: 
      if ret is not None:
        raise Exception("Duplicate bee %s" % str((wname,)+r[0]))
      if "@"+wname in beewraps: 
        if nosub == False:
          wname = "@"+wname
        else:
          wname = "$"+wname
      ret = (wname,)+r[0], r[1]
      
  if ret is not None: return ret  
  
  return None, None


class connect(beehelper):
  def getinstance(self,__parent__=None):
    return self.__class__(self.source_original, self.target_original, self.nosub)
  def set_parameters(self, name, parameters): pass
  def __init__(self, source, target, nosub=False):

    if isinstance(source, proxy):
      source = source.source
    if isinstance(source, tuple) and len(source) >= 2:
      if isinstance(source[-1], proxy):
        source = source[:-1] + (source[-1].source,)

    if isinstance(target, proxy):
      target = target.target
    if isinstance(target, tuple) and len(target) >= 2:
      if isinstance(target[-1], proxy):
        target = target[:-1] + (target[-1].target,)

    self.source_original = source
    self.target_original = target
    self.nosub = nosub

    self.source = source
    self.target = target
    self.bound_source = True
    self.bound_target = True
    
    self.connect_contexts = None
    #bees with a connect_contexts attribute get closed before any other context
    #only fill this in case of worker connections (the other ones don't have their own contexts)
       
    if isinstance(source, str):
      self.source_name = source
      self.source_io = None
    elif isinstance(source, tuple):    
      if len(source) <= 2:
        self.source_name = source[0]      
        if len(source) == 2: self.source_io = source[1]
        if hasattr(self.source_name, "__get_beename__"):
          self.bound_source = False
      else:
        self.source_name = source[:-1]
        self.source_io = source[-1]
        if hasattr(self.source_name[0], "__get_beename__"):
          self.bound_source = False
    elif hasattr(source, "__get_beename__"):
      self.source_name = source
      self.source_io = None
      self.bound_source = False
    else:
      if hasattr(source, "_wrapped_hive") and not isinstance(source._wrapped_hive, tuple):
        if not hasattr(source, "instance") or isinstance(source.instance, tuple):
          beename = '<' + source.__name__ +'>'          
          import inspect
          fr = inspect.currentframe().f_back.f_back
          for k in fr.f_locals.keys():
            if fr.f_locals[k] ==  source: 
              beename = "'" + k + "'"
              break
        raise TypeError("You must initialize %s, add ()" % beename)
      raise TypeError(source)

    if isinstance(target, str):
      self.target_name = target
      self.target_io = None
    elif isinstance(target, tuple):    
      if len(target) <= 2:
        self.target_name = target[0]      
        if len(target) == 2: self.target_io = target[1]
        if hasattr(self.target_name, "__get_beename__"):
          self.bound_target = False
      else:
        self.target_name = target[:-1]      
        self.target_io = target[-1]
        if hasattr(self.target_name[0], "__get_beename__"):
          self.bound_target = False
    elif hasattr(target, "__get_beename__"):
      self.target_name = target
      self.target_io = None
      self.bound_target = False
    else: 
      if hasattr(target, "_wrapped_hive") and not isinstance(target._wrapped_hive, tuple):
        if not hasattr(target, "instance") or isinstance(target.instance, tuple):
          beename = '<' + target.__name__ +'>'          
          import inspect
          fr = inspect.currentframe().f_back.f_back
          for k in fr.f_locals.keys():
            if fr.f_locals[k] ==  target: 
              beename = "'" + k + "'"
              break
        raise TypeError("You must initialize %s, add ()" % beename)    
      raise TypeError(target)

    if isinstance(self.source_io, str) and self.source_io.find(".") > -1:
      sp = tuple(self.source_io.split("."))
      s = self.source_name
      if isinstance(s, str): s = (s,)
      self.source_name = s + sp[:-1]
      self.source_io = sp[-1]
    if isinstance(self.target_io, str) and self.target_io.find(".") > -1:
      sp = tuple(self.target_io.split("."))
      t = self.target_name
      if isinstance(t, str): t = (t,)
      self.target_name = t + sp[:-1]
      self.target_io = sp[-1]

  def bind(self):
    currhive = libcontext.get_curr_context().subcontext
    
    if not self.bound_source:    
      beename, self.source_io = search_beename(self.source_name, currhive, self.source_io, self.nosub)
      if beename is None:
        if not isinstance(self.source_name.beename, str): return
        v = getattr(currhive, self.source_name.beename)
        if isinstance(v,tuple) and len(v) == 2 and v[0] is currhive:                  
          raise ValueError("Cannot find '%s' in hive" % self.source_name.beename)
        else: return
      self.source_name = beename
      if self.source_io != None:
        self.source = (self.source_name, self.source_io)
      else: self.source = self.source_name
      self.bound_source = True
    if not self.bound_target:
      beename, self.target_io = search_beename(self.target_name, currhive, self.target_io, self.nosub)
      if beename is None: 
        v = getattr(currhive, self.target_name.beename)
        if isinstance(v,tuple) and len(v) == 2 and v[0] is currhive:                  
          raise ValueError("Cannot find '%s' in hive" % self.target_name.beename)
        else: return  
      self.target_name = beename
      if self.target_io != None:
        self.target = (self.target_name, self.target_io)
      else: self.target = self.target_name      
      self.bound_target = True      
  def get_source_candidates(self, sourcecontext):
    source_plugin_candidates, source_socket_candidates = [], []    
    if self.source_io != None:
      found = False
      if self.source_io in sourcecontext.plugins:
        source_plugin_candidates = [self.source_io]
        found = True
      else:        
        worker = False
        for p in sourcecontext.plugins:
          if not isinstance(p, tuple): 
            continue
          if p[1] != "output": continue
          pp = p[2]
          if self.nosub == False and pp.startswith("@"): pp = pp.lstrip("@")
          if pp != self.source_io: continue
          source_plugin_candidates = [p]
          found = True
          worker = True
          break
        else:          
          source_plugin_candidates = []
      if not found:
        if self.source_io in sourcecontext.sockets:
          source_socket_candidates = [self.source_io]
        else:
          worker = False
          for p in sourcecontext.sockets:
            if not isinstance(p, tuple): 
              continue
            if p[1] != "output": continue
            pp = p[2]
            if self.nosub == False and pp.startswith("@"): pp = pp.lstrip("@")
            if pp != self.source_io: continue
            source_socket_candidates = [p]
            source_plugin_candidates = []
            worker = True
            break
          else:
              raise TypeError("%s has no socket or plugin '%s'" % (sourcecontext.contextname,self.source_io))
    else:
      worker = True          
      found = False
      for p in sourcecontext.plugins:
        if not isinstance(p, tuple): 
          worker = False
          continue
        if p[0] not in ("bee", "evin", "evout","evexc"): 
          worker = False
          continue
        if p[1] != "output": continue
        source_plugin_candidates.append(p)
        found = True
      if not found:
        if not worker: source_plugin_candidates = sourcecontext.plugins.keys()
      worker = True                 
      found = False
      for p in sourcecontext.sockets:
        if not isinstance(p, tuple): 
          worker = False
          continue
        if p[0] not in ("bee", "evin", "evout", "evexc"): 
          worker = False
          continue
        if p[1] != "output": continue
        if p[2].startswith("__") and p[2].endswith("__"): continue
        source_socket_candidates.append(p)
        found = True
      if not found:
        if not worker: source_socket_candidates = sourcecontext.sockets.keys()
    return source_socket_candidates, source_plugin_candidates
  
  def get_target_candidates(self, targetcontext):
    target_plugin_candidates, target_socket_candidates = [], []        
    if self.target_io != None:
      found = False
      if self.target_io in targetcontext.plugins:
        target_plugin_candidates = [self.target_io]
        found = True
      else:        
        worker = False            
        for p in targetcontext.plugins:
          if not isinstance(p, tuple): 
            continue
          if p[1] != "antenna": continue
          pp = p[2]
          if self.nosub == False and pp.startswith("@"): pp = pp.lstrip("@")
          if pp != self.target_io: continue
          target_plugin_candidates = [p]
          worker = True
          found = True
          break
        else:
          target_plugin_candidates = []
      if not found:      
        if self.target_io in targetcontext.sockets:
          target_socket_candidates = [self.target_io]
        else:
          worker = False              
          for p in targetcontext.sockets:
            if not isinstance(p, tuple): 
              continue
            if p[1] != "antenna": continue
            pp = p[2]
            if self.nosub == False and pp.startswith("@"): pp = pp.lstrip("@")
            if pp != self.target_io: continue
            target_socket_candidates = [p]
            target_plugin_candidates = []
            worker = True            
            break
          else:
            print("Source:", self.source_name, self.source_io)
            print("Target:", self.target_name, self.target_io)
            print("Target plugins:", list(targetcontext.plugins.keys()))
            print("Target sockets:", list(targetcontext.sockets.keys()))
            raise TypeError("%s has no socket or plugin '%s'" % (targetcontext.contextname,self.target_io))
    else:
      worker = True              
      found = False
      for p in targetcontext.plugins:
        if not isinstance(p, tuple): 
          worker = False
          continue
        if p[0] not in ("bee", "evin", "evout","evexc"): 
          worker = False
          continue
        if p[1] != "antenna": continue
        if p[2].startswith("__") and p[2].endswith("__"): continue
        target_plugin_candidates.append(p)
        found = True
      if not found:
        if not worker: target_plugin_candidates = targetcontext.plugins.keys()                  
      worker = True                  
      found = False      
      for p in targetcontext.sockets:
        if not isinstance(p, tuple): 
          worker = False
          continue
        if p[0] not in ("bee", "evin", "evout","evexc"): 
          worker = False
          continue
        if p[1] != "antenna": continue
        target_socket_candidates.append(p)
        found = True
      if not found:
        if not worker: target_socket_candidates = targetcontext.sockets.keys()
    return target_socket_candidates, target_plugin_candidates    
  
  def _get_sourcecontextname(self):
    if isinstance(self.source_name, str) or isinstance(self.source_name, tuple):   
      z = undollar(self.source_name)
      sourcecontextname = libcontext.add_contextnames(libcontext.get_curr_contextname(), z)
    else:
      sourcecontextname = self.source_name.contextname()
    return sourcecontextname
      
  def _get_targetcontextname(self):
    if isinstance(self.target_name, str) or isinstance(self.target_name, tuple): 
      z = undollar(self.target_name)
      targetcontextname = libcontext.add_contextnames(libcontext.get_curr_contextname(), z)
    else:
      targetcontextname = self.target_name.contextname()
    return targetcontextname
       
  def connect_worker_worker(self):    
    sourcecontextname = self._get_sourcecontextname()
    sourcecontext = libcontext.get_context(sourcecontextname)
    targetcontextname = self._get_targetcontextname()
    targetcontext = libcontext.get_context(targetcontextname)

    source_socket_candidates, source_plugin_candidates = self.get_source_candidates(sourcecontext)
    target_socket_candidates, target_plugin_candidates = self.get_target_candidates(targetcontext)
    
    spmatch,spmatch_wrongtype = [],[]
    psmatch,psmatch_wrongtype = [],[]
        
    
    w1, w2 = False, False
    for m1,m2,match,match_wrongtype in (
      (source_socket_candidates, target_plugin_candidates, spmatch,spmatch_wrongtype),
      (source_plugin_candidates, target_socket_candidates, psmatch,psmatch_wrongtype),
    ):
      for mm in m1:
        if isinstance(mm, tuple) and len(mm) and mm[0] == "bee":
          w1 = True
          break
      for mm in m2:
        if isinstance(mm, tuple) and len(mm) and mm[0] == "bee":
          w2 = True
          break

    for m1,m2,match,match_wrongtype in (
      (source_socket_candidates, target_plugin_candidates, spmatch,spmatch_wrongtype),
      (source_plugin_candidates, target_socket_candidates, psmatch,psmatch_wrongtype),
    ):
      if not (len(m1) and len(m2)): continue
      if not w1 or not w2:
        for mm1 in m1:
          if w1 and (not isinstance(mm1, tuple) or len(mm1) < 4): continue
          if w1 and mm1[3] != "exception": continue
          for mm2 in m2:
            if w2 and (not isinstance(mm2, tuple) or len(mm2) < 4): continue
            if w2 and mm2[3] != "exception": continue
            match.append((mm1, mm2))
      else:
        for mm1 in m1:
          if mm1[0] != "bee": continue
          for mm2 in m2:
            if mm2[0] != "bee": continue
            if mm1[2] != "connection" and len(mm1) > 3 and len(mm2) > 3 and typecompare(mm1[3],mm2[3]): 
              match.append((mm1, mm2))
            else: match_wrongtype.append((mm1,mm2))
        
    matches = spmatch + psmatch
    if len(matches) == 0:
      wrongmatches = spmatch_wrongtype + psmatch_wrongtype
      if len(wrongmatches) == 1:
        if len(spmatch_wrongtype):
          sp = spmatch_wrongtype[0]
          cand = "  socket %s\n  plugin %s\n" % (sp[0], sp[1])
        elif len(psmatch_wrongtype):
          ps = psmatch_wrongtype[0]
          cand = "  plugin %s\n  socket %s\n" % (ps[0], ps[1])                  
        raise TypeError("Error in connect %s - %s\nType mismatch:\n%s\n"% (self.source, self.target,cand))
      else:
        raise TypeError("Error in connect %s - %s\nNo matches found" % (self.source, self.target))
    elif len(matches) > 1: 
      cand = ""
      for sp in spmatch:
        cand += "socket %s - plugin %s\n" % (sp[0], sp[1])
      for ps in psmatch:
        cand += "plugin %s - socket %s\n" % (ps[0], ps[1])        
      raise TypeError("Ambiguity in connect %s - %s\nCandidates:\n%s\n" % (self.source, self.target,cand))
    else:
      z1 = undollar(self.source_name)
      z2 = undollar(self.target_name)
      if len(spmatch):
        self.connect_contexts = libcontext.connect((z1, spmatch[0][0]),(z2, spmatch[0][1])).place() 
      else:
        self.connect_contexts = libcontext.connect((z2, psmatch[0][1]),(z1, psmatch[0][0])).place()  
      self.connect_contexts[0].connect = self
      self.connect_contexts[1].connect = self
      
  def connect_evout_evin(self, newsource, newtarget):    
    exc = isinstance(self.source, evexccontext) or isinstance(self.target, evexccontext)
    if exc:
      newtarget.import_socket(self.source, "exception")
      newtarget.import_plugin(self.target, "read-exception", "exception")
    
      newsource.import_socket(self.source, "exception")
      newsource.import_plugin(self.target, "read-exception", "exception")
    
    else:  
      newsource.connection = self.target
      newtarget.connection = self.source
      
  def connect_evout_worker(self, newsource, newtarget):
    contype = "event"
    if isinstance(self.source, evexccontext): contype = "exception"
        
    targetcontextname = self._get_targetcontextname()
    targetcontext = libcontext.get_context(targetcontextname)   
    
    target_socket_candidates, target_plugin_candidates = self.get_target_candidates(targetcontext)    
    matches = []
    for p in target_plugin_candidates:      
      if isinstance(p, tuple) and len(p) == 4: 
        if p[0] == "bee" and p[1] == "antenna" and typecompare(p[3],contype):
          matches.append(p)
    if len(matches) == 0:
      raise TypeError("Error in connect %s - %s\nNo antennas with type '%s' found in target" % (self.source_name, self.target, contype))
    elif len(matches) > 1:
      cand = ""
      for c in matches:
        cand += "%s - %s\n" % (self.source_name, c)
      raise TypeError("Ambiguity in connect %s - %s\nCandidates:\n%s\n" % (self.source_name, self.target,cand))
    
    newtarget.import_socket(self.source, contype, matches[0])
    newtarget.import_plugin(targetcontext, matches[0])
    
    newsource.import_socket(self.source, contype)
    newsource.import_plugin(targetcontext, matches[0], contype)

  def connect_worker_evin(self, newsource, newtarget):
    contype = "event"
    if isinstance(self.target, evexccontext): contype = "exception"
  
    sourcecontextname = self._get_sourcecontextname()
    sourcecontext = libcontext.get_context(sourcecontextname)
  
    source_socket_candidates, source_plugin_candidates = self.get_source_candidates(sourcecontext)    
    matches = []
    for s in source_socket_candidates:      
      if isinstance(s, tuple) and len(s) == 4: 
        if s[0] == "bee" and s[1] == "output" and typecompare(s[3],contype):
          matches.append(s)
    if len(matches) == 0:
      raise TypeError("Error in connect %s - %s\nNo outputs with type '%s' found in source" % (self.source, self.target_name, contype))
    elif len(matches) > 1:
      cand = ""
      for c in matches:
        cand += "%s - %s\n" % (c, self.target_name)
      raise TypeError("Ambiguity in connect %s - %s\nCandidates:\n%s\n" % (self.source, self.target_name,cand))      
    
    newtarget.import_plugin(self.target, contype)
    newtarget.import_socket(sourcecontext, matches[0], contype)
    
    newsource.import_plugin(self.target, contype, matches[0])
    newsource.import_socket(sourcecontext, matches[0])
    
  def set_parent(self, parent):
    self.parentbees = [n[1] for n in parent.bees]
    self.parent = parent
    
  def place(self):
    from libcontext import new_abscontextname, add_contextnames
    from . import BuildError
    #try:
    #  self.bind()
    #except BuildError, e:
    # return
    self.bind()    
    if not self.bound_source or not self.bound_target: return        
    self.parentcontext = libcontext.get_curr_context()
    
    if self.source_io is not None:
      snam = self.source_io
      if isinstance(snam, str): snam = (snam,)
      for n in range(len(snam)-1):
        if snam[n] in ("evin", "evout","evexc"): break
        source_name2 = libcontext.add_contextnames(self.source_name, snam[:n+1])
        try:
          libcontext.get_context(libcontext.abscontextname(source_name2))
        except KeyError:
          break
      else: n = len(snam)-1
      snam = snam[n:]
      if n: 
        self.source_name = libcontext.add_contextnames(self.source_name, snam[:n])
        if len(snam) == 1: snam = snam[0]
        elif not len(snam): snam = None
        self.source_io = snam
    sourcecontextname = self._get_sourcecontextname()
    sourcecontext = libcontext.get_context(sourcecontextname)
    self.sourcecontext = sourcecontext

    if self.target_io is not None:
      tnam = self.target_io
      if isinstance(tnam, str): tnam = (tnam,)
      for n in range(len(tnam)-1):
        if tnam[n] in ("evin", "evout","evexc"): break
        target_name2 = libcontext.add_contextnames(self.target_name, tnam[:n+1])
        try:
          libcontext.get_context(libcontext.abscontextname(target_name2))
        except KeyError:
          break
      else: n = len(tnam)-1
      tnam = tnam[n:]
      if n: 
        self.target_name = libcontext.add_contextnames(self.target_name, tnam[:n])
        if len(tnam) == 1: tnam = tnam[0]
        elif not len(tnam): tnam = None
        self.target_io = tnam

    targetcontextname = self._get_targetcontextname()
    targetcontext = libcontext.get_context(targetcontextname)
    self.targetcontext = targetcontext
    
    evsource = False
    try: 
      sourceiocontextname = libcontext.add_contextnames(sourcecontextname, self.source_io)
      sourceiocontext = libcontext.get_context(sourceiocontextname)
      evsource = isinstance(sourceiocontext, evoutcontext) or isinstance(sourceiocontext, evexccontext)     
    except KeyError:
      pass

    evtarget = False
    try:             
      targetiocontextname = libcontext.add_contextnames(targetcontextname, self.target_io)
      targetiocontext = libcontext.get_context(targetiocontextname)
      evtarget = isinstance(targetiocontext, evincontext) or isinstance(targetiocontext, evexccontext)     
    except KeyError:
      pass
          
    if (not evsource) and (not evtarget):
      return self.connect_worker_worker()
    else:    
      if evsource and evtarget:
        self.source = sourceiocontext
        self.target = targetiocontext          
        newsourcecontextname = new_abscontextname(add_contextnames(sourceiocontextname, "<<evconnect>>"))
        newtargetcontextname = new_abscontextname(add_contextnames(targetiocontextname, "<<evconnect>>"))    
        connectfunc = self.connect_evout_evin
      elif evsource and (not evtarget):
        self.source = sourceiocontext    
        newsourcecontextname = new_abscontextname(add_contextnames(sourceiocontextname, "<<connect>>"))
        newtargetcontextname = new_abscontextname(add_contextnames(targetcontextname, "<<connect>>"))            
        connectfunc = self.connect_evout_worker
      elif (not evsource) and evtarget:
        self.target = targetiocontext      
        newsourcecontextname = new_abscontextname(add_contextnames(sourcecontextname, "<<connect>>"))
        newtargetcontextname = new_abscontextname(add_contextnames(targetiocontextname, "<<connect>>"))                    
        connectfunc = self.connect_worker_evin              
      else: raise Exception #Never happens...
      newsourcecontext = connectioncontext(*newsourcecontextname, absolute=True) 
      newsourcecontext.connect = self   
      newsourcecontext.import_all_from_parent = True
      newtargetcontext = connectioncontext(*newtargetcontextname, absolute=True)
      newtargetcontext.import_all_from_parent = True
      newtargetcontext.connect = self   
      connectfunc(newsourcecontext, newtargetcontext)        
      
