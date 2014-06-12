def workerid_to_nodename(workerid):
  return workerid.split(".")[-1]

class WorkerInstance(object):
  _morphing = {
    "evin":  {"default":"default_evio","plain":"plain_evio","simplified":"default_evio"},
    "evout": {"default":"default_evio","plain":"plain_evio","simplified":"default_evio"},
    "everr": {"default":"default_evio","plain":"plain_evio","simplified":"default_evio"},
    "evexc": {"default":"default_evio","plain":"plain_evio","simplified":"default_evio"},
  }
  def __init__(self, type_, profiles, paramnames, paramtypelist, block, guiparams):
    self.type = type_
    self.profiles = profiles
    self.paramnames = paramnames
    self.paramtypelist = paramtypelist
    self.block = block
    self.guiparams = guiparams
    self.curr_profile = None
    self.curr_blockvalues = []
  def _get_morph(self, attribute):
    if attribute not in self._morphing: 
      if self.curr_profile == "simplified": 
        return "default"
      else:
        return None
    m = self._morphing[attribute]
    if self.curr_profile not in m: return None
    return m[self.curr_profile]
  def profile(self):
    return self.profiles[self.curr_profile]
  def check_antenna(self, attribute):
    if self.block is not None and self.block.io == "antenna":
      if attribute in self.curr_blockvalues: return None #OK
    prof = self.profiles[self.curr_profile]
    attribs, mapping = prof
    at = mapping.inmap[attribute]
    for a in attribs:
      if a.name == at:
        if a.inhook is not None:
          return None #OK
        else:
          break  
    ret = self._get_morph(attribute)
    if ret is None:
      raise KeyError(attribute)
    return ret  
  def check_output(self, attribute):
    if self.block is not None and self.block.io == "output":
      if attribute in self.curr_blockvalues: return None #OK
    prof = self.profiles[self.curr_profile]
    attribs, mapping = prof
    at = mapping.outmap[attribute]
    for a in attribs:
      if a.name == at:
        if a.outhook is not None:
          return None #OK
        else:
          break  
    ret = self._get_morph(attribute)
    if ret is None:
      raise KeyError(attribute)
    return ret  
  def update_blockvalues(self, blockvalues):
    self.curr_blockvalues = blockvalues
    
from ..HGui import Node

class WorkerInstanceManager(object):
  def __init__(self, canvas):
    self._canvas = canvas
    self.observers_selection = canvas.observers_selection
    self.observers_remove = canvas.observers_remove
    self._workerinstances = {}
    self._workerparams = {}
    self._empties = set()
    self.default_profile = "default"
  def add_workerinstance(self, workerid, workerinstance,x,y):
    assert workerid not in self._workerinstances, workerid
    prof = self.default_profile
    if prof not in workerinstance.profiles: prof = "default"
    attribs, mapping = workerinstance.profiles[prof]
    nodename = workerid_to_nodename(workerid)
    node = Node(nodename, (x,y), attribs)
    self._canvas.add_node(workerid, node)
    workerinstance.curr_profile = prof
    self._workerinstances[workerid] = workerinstance
  def select(self, workerids):
    self._canvas.select(workerids)

  def _morph_worker(self, workerid, attributes, maps):
    wi = self._workerinstances[workerid]
    if wi.block is not None:
      if wi.block.io == "antenna": cmap = maps[0]
      elif wi.block.io == "output": cmap = maps[1]
      else: raise Exception(wi.block.io)
      if cmap is not None: cmap.update(wi.block.blockmap)

    nodename = workerid_to_nodename(workerid)
    node0 = self._canvas.get_node(workerid)
    x,y = node0.position
    newnode = Node(nodename, (x,y), attributes)      
    self._canvas.morph_node(workerid, newnode, maps[0], maps[1])
  
  def morph_worker(self, workerid, morph):
    wi = self._workerinstances[workerid]
    
    m0 = wi.profile()
    m1 = wi.profiles[morph]
    map0, map1 = m0[1], m1[1]    
    maps = []
    for at in "in", "out":
      cmap = {}
      mapr = getattr(map0,"_"+at+"mapr")
      mapnew = getattr(map1,"_"+at+"map")
      for v,k in mapr.items():
        if k is None: continue
        if mapnew[k] is None: continue 
        vv = mapnew[k]
        cmap[v] = vv
      maps.append(cmap)

    self._morph_worker(workerid, m1[0], maps)  
    
    wi.curr_profile = morph
    if workerid in self._workerparams:
      self.set_parameters(workerid, self._workerparams[workerid])
  def worker_update_blockvalues(self, workerid, blockvalues):
    wi = self._workerinstances[workerid]
    assert wi.block is not None
    block_attributes = wi.block.attributes

    attributes = list(wi.profile()[0])
    for blockvalue in blockvalues:
      if not blockvalue: continue
      attribute = block_attributes[blockvalue]
      attributes.append(attribute)
    
    wi.update_blockvalues(blockvalues)
    self._morph_worker(workerid, attributes, (None, None))
  def get_blockvalues(self, workerid):
    wi = self._workerinstances[workerid]
    if wi.block is None: return None
    return wi.curr_blockvalues
    
  def add_connection(self, id_, start, end, interpoints = []):
    start_id, start_attr = start
    wi_start = self._workerinstances[start_id]
    morph = wi_start.check_output(start_attr)
    if morph is not None: self.morph_worker(start_id, morph)
    
    end_id, end_attr = end
    wi_end = self._workerinstances[end_id]
    morph = wi_end.check_antenna(end_attr)
     
    if morph is not None: self.morph_worker(end_id, morph)
    
    do_map_start = True
    if wi_start.block is not None:
      if wi_start.block.io == "output":
       if start[1] in wi_start.block.tree:
         do_map_start = False
    if do_map_start:
      map_start = wi_start.profile()[1].outmap
      m_start = map_start[start[1]]
    else:
      m_start = start[1]

    do_map_end = True
    if wi_end.block is not None:
      if wi_end.block.io == "antenna":
       if end[1] in wi_end.block.tree:
         do_map_end = False
    if do_map_end:
      map_end = wi_end.profile()[1].inmap
      m_end = map_end[end[1]]      
    else:
      m_end = end[1]
    
    startm = (start[0], m_start)
    endm = (end[0], m_end)
    self._canvas.add_connection(id_, startm, endm, interpoints)    
  def get_node(self, workerid):
    node = self._canvas.get_node(workerid)
    try:
      wi = self._workerinstances[workerid]
      mapping = wi.profile()[1]
    except KeyError: #empty
      mapping = None  
    return node, mapping
  def get_workerinstance(self, workerid):
    return self._workerinstances[workerid]
  def get_workerinstances(self):
    return self._workerinstances.keys()

  def get_connections(self):
    return self._canvas.get_connections()
  def get_connection_ids(self):
    return self._canvas.get_connection_ids()
  def has_connection(self, workerid, io, segio):
    """
    Returns whether a worker has one or more connections to the specified segio
     workerid: the ID of the worker
     io: "antenna" or "output"
     segio: the name of the antenna or output
    """  
    assert io in ("antenna", "output"), io
    for con in self._canvas.get_connections():
      if io == "antenna":
        w, seg = con.end_node, con.end_attribute
      else:
        w, seg = con.start_node, con.start_attribute
      if w == workerid and segio == seg: return True
    return False    
            
  def add_empty(self, workerid, x, y):
    nodename = workerid_to_nodename(workerid)
    node = Node(nodename, (x,y), [], empty = True)
    self._canvas.add_node(workerid, node)
    self._empties.add(workerid)
  def gui_removes_workerinstance(self, workerid):
    if workerid in self._empties:
      self._empties.remove(workerid)
    else:  
      workerinstance = self._workerinstances.pop(workerid)
      self._workerparams.pop(workerid, None)
  def remove_workerinstance(self, workerid):
    workerinstance = self._workerinstances.pop(workerid)
    self._canvas.remove_node(workerid)
    self._workerparams.pop(workerid, None)
  def remove_empty(self, workerid):
    self._canvas.remove_node(workerid)
    self._empties.remove(workerid)
  def rename_workerinstance(self, old_workerid, new_workerid):
    new_nodename = workerid_to_nodename(new_workerid)
    self._canvas.rename_node(old_workerid, new_workerid, new_nodename)  
    inst = self._workerinstances.pop(old_workerid)
    self._workerinstances[new_workerid] = inst
  def set_parameters(self, workerid, params):
    self._workerparams[workerid] = params
    wi = self._workerinstances[workerid]
    pmapping = wi.profile()[1].pmap
    #print("PARAMS", params, pmapping)
    mparams = {}
    for p in params:
      mp = pmapping[p]
      if mp is None: continue
      mparams[p] = params[mp]
    for p,v in mparams.items():
      self._canvas.set_attribute_value(workerid, p, v)