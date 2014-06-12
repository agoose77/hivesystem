from __future__ import print_function
from .context import bee_or_evexc, retrieve_sockets, retrieve_plugins, matchreport0
from .contextmatch import contextmatch, import_sockets, import_plugins

def plocksortfunc(name):
  if isinstance(name, tuple):
    strings = ()
    numbers = ()
    for r in name:
      n,s = plocksortfunc(r)
      numbers += n
      strings += s
    ret = (numbers, strings)
  else:
    if isinstance(name,str): name = (name,)
    ret = ((-len(name),), name)
  return ret

def matchmake(context, subcontexts, subcontextnames):
  if not isinstance(context.contextname, str):
    if len(subcontexts) <= 1: return
  
  contextdict = dict(zip(subcontextnames, subcontexts))
  
  #build a dict to find the parent of a context (by name)
  parentdict = {}  
  for subcontextname in subcontextnames:
    assert isinstance(subcontextname, tuple) or subcontextname == context.contextname
    pcontextname = subcontextname[:-1]
    if len(pcontextname) == 1:
      assert pcontextname[0] == context.contextname, pcontextname[0]
      parentdict[subcontextname] = context.contextname
    else:
      if pcontextname not in contextdict: continue
      parentdict[subcontextname] = pcontextname
    
  #build a standard network of connected hive.frame contexts  
  std_network = {context.contextname:context}
  build_network(std_network, subcontexts, subcontextnames, parentdict)
  
  #build networks for the contexts that are not in the standard network
  from .context import context as class_context
  from .evcontext import evcontext
  networks = [std_network]  
  remaining = [(sub,name) for sub,name in zip(subcontexts,subcontextnames) \
   if isinstance(sub, class_context) \
    and not isinstance(sub, evcontext) \
    and not isinstance(sub, evcontext) \
    and not name[-1].startswith("<<") \
    and name not in std_network]  
  while len(remaining):
    rsubcontexts = [v[0] for v in remaining]
    rsubcontextnames = [v[1] for v in remaining]
    new_network = {rsubcontextnames[-1]:rsubcontexts[-1]}
    build_network(new_network, rsubcontexts, rsubcontextnames, parentdict)
    networks.append(new_network)
    remaining = [(sub,name) for sub,name in remaining if name not in new_network]  
  
  #sort networks according to maximum  highest priority (lowest index) of their members
  nwprior = {}
  for netw in networks:
    prior = 99999999
    for k in netw:
      cprior = subcontextnames.index(k)
      if cprior < prior: prior = cprior
    nwprior[id(netw)] = prior
  networks.sort(key=lambda netw: nwprior[id(netw)])
  in_network = {}
  for netwnr, netw in enumerate(networks):
    for k in netw:
      sub = netw[k]
      in_network[sub] = netwnr

  """
  #resolve non-ev, non-worker-worker connections (rare)
  for snr,sub in enumerate(subcontexts):
    if not sub.contextname[-1].startswith("<<connect"): continue
    if len(sub.socket_imports) == 0: continue
    assert len(sub.socket_imports) == 1
    assert len(sub.plugin_imports) == 1
    si, pi = sub.socket_imports[0], sub.plugin_imports[0]
    s, p = si[1], pi[1]
    if (bee_or_evexc(s) or s == "exception") and \
     (bee_or_evexc(p) or p == "exception"):
      continue 
    cs, cp = si[0], pi[0]
    cs.import_plugin(cp, p, s)
    cp.import_socket(cs, s, p)
  """
  
  #build lists of evcontexts and evconnects
  evcontexts = set()
  evmap = {}
  for snr,sub in enumerate(subcontexts):
    if isinstance(sub, evcontext): 
      evcontexts.add(sub)
      k = parentdict[sub.contextname]
      if k not in evmap: evmap[k] = {}
      evmap[k][sub.contextname[-1]] = sub
   
  evconnects = set()    
  evconmap_fwd = {}
  evconmap_back = {}
  for sub in subcontexts:
    evconmap_fwd[sub] = []
    evconmap_back[sub] = []
  for snr,sub in enumerate(subcontexts):
    sname = sub.contextname
    if sname[-1].startswith("<<evconnect"):
      assert len(sub.sockets) == 0, sub.sockets
      assert len(sub.plugins) == 0, sub.plugins
      evconnects.add(sub)
      con = sub.connect
      srcname = con.source.contextname      
      srcname, evsrc = srcname[:-1], srcname[-1]
      if len(srcname) == 1: srcname = srcname[0]
      tarname = con.target.contextname      
      tarname, evtar = tarname[:-1], tarname[-1]
      if len(tarname) == 1: tarname = tarname[0]
      src, tar = contextdict[srcname], contextdict[tarname]
      evconmap_fwd[src].append((evsrc, tar, tarname, evtar))      
      evconmap_back[tar].append((evtar, src, srcname, evsrc))      

  #resolve evcontexts (evexc)
  for snr,sub in enumerate(subcontexts):
    if sub not in evcontexts: continue
    pname, evname = sub.contextname[:-1], sub.contextname[-1]
    if evname != "evexc": continue
    if len(pname) == 1: pname = pname[0]
    pcontext = contextdict[pname]
    for s in pcontext.sockets:
      if not isinstance(s, tuple): continue
      if s[0] != evname: continue
      s2 = s[1:]
      if len(s2) == 1: s2 = s2[0]
      #for sock in pcontext.sockets[s]:
      for x,sock in retrieve_sockets(pcontext, s):
        sub.socket(s2, sock)
    for p in pcontext.plugins:
      if not isinstance(p, tuple): continue
      if p[0] != evname: continue
      p2 = p[1:]
      if len(p2) == 1: p2 = p2[0]
      #for plug in pcontext.plugins[p]:
      for x,plug in retrieve_plugins(pcontext, p):      
        sub.plugin(p2, plug)

  #resolve ev connections
  resolve_evmap(subcontexts, evconmap_fwd)
    
  #spread plugins and sockets around the network
  orisocks = {}
  oriplugs = {}
  matchsocks = {}
  matchplugs = {}
  for sub in subcontexts:
    csocks = {}
    cplugs = {}
    cmsocks = {}
    cmplugs = {}
    for s in sub.sockets.keys():
      cmplugs[s] = []
    for p in sub.plugins.keys():
      cmsocks[p] = []

    for s in sub.sockets.keys():
      csocks[s] = list(sub.sockets[s])
      cmsocks[s] = list(sub.sockets[s])
    for p in sub.plugins.keys():
      cplugs[p] = list(sub.plugins[p])
      cmplugs[p] = list(sub.plugins[p])

    orisocks[sub] = csocks
    oriplugs[sub] = cplugs
    matchsocks[sub] = cmsocks
    matchplugs[sub] = cmplugs
    
  for snr,sub in enumerate(subcontexts):
    sname = sub.contextname
    if sub not in in_network: continue
    subs = list(matchsocks[sub].items())
    subs.sort(key=lambda v:plocksortfunc(v[0]))
    subp = list(matchplugs[sub].items())
    subp.sort(key=lambda v:plocksortfunc(v[0]))
    for snr2,sub2 in list(enumerate(subcontexts))[snr+1:]:      
      if sub2 is sub: continue
      if sub2 not in in_network: continue
      if in_network[sub] != in_network[sub2]: continue
      sub2s = orisocks[sub2]
      sub2p = oriplugs[sub2]
      for s,socks in subs:
        if bee_or_evexc(s) or s == "exception": continue
        try:
          socks2 = sub2s[s]
        except KeyError:
          continue
        socks[:] = socks + socks2
      for p,plugs in subp:
        if bee_or_evexc(p) or p == "exception": continue
        try:
          plugs2 = sub2p[p]
        except KeyError:
          continue
        plugs[:] = plugs + plugs2
  
  
  #resolve explicit imports
  network_updated_s = []
  network_updated_p = []
  for netw in networks:
    updated_s, updated_p = set(), set()
    for subname, sub in netw.items():
      updated_s.update(set(matchsocks[sub].keys()))
      updated_p.update(set(matchplugs[sub].keys()))
    network_updated_s.append(updated_s)
    network_updated_p.append(updated_p)  

  anychanged = True
  while any(network_updated_s) or any(network_updated_p) or anychanged:
    anychanged = False        
    network_updated2_s = [set() for netw in networks]
    network_updated2_p = [set() for netw in networks]
    for snr,sub in enumerate(subcontexts):
      if sub not in in_network: continue
      if sub.contextname[-1].startswith("<<"): continue
      imports = [("socket",imp) for imp in sub.socket_imports] \
       + [("plugin",imp) for imp in sub.plugin_imports] 
      nwindex = in_network[sub]
      nw = networks[nwindex]
      for mode,imp in imports:
        network_updated = network_updated_s if mode == "socket" else network_updated_p
        network_updated2 = network_updated2_s if mode == "socket" else network_updated2_p
        contextinstance, name, newname, optional = imp
        if isinstance(contextinstance, evcontext):
          pcontextname = contextinstance.contextname[:-1]
          if len(pcontextname) == 1: pcontextname = pcontextname[0]
          pname = name
          if isinstance(pname, str): pname = (pname,)
          pname = (contextinstance.contextname[-1],) + pname
        else:
          pcontextname = contextinstance.contextname          
          pname = name          
        
        pcontext = contextdict[pcontextname] 
        nwindex2 = None
        if pcontext in in_network: nwindex2 = in_network[pcontext]
        if nwindex2 is not None:
          if pname not in network_updated[nwindex2]: continue         
        
        if bee_or_evexc(newname):         
          ok = False
          spread = False
        else:
          ok = True
          spread = True
          if nwindex2 == nwindex:
            if pname == newname:
              spread = False
              ok = False
        if not ok: continue

        changed = False
        
        if pcontext not in subcontexts:
          ps = pcontext.sockets if mode == "socket" else pcontext.plugins
        else:
          ps = matchsocks[pcontext] if mode == "socket" else matchplugs[pcontext]
        if pname not in ps or len(ps[pname]) == 0:
          #print("NOT FOUND", pcontextname, mode, pname)
          continue

        subps0 = matchsocks[sub] if mode == "socket" else matchplugs[sub]
        if newname not in subps0: subps0[newname] = []
        subps = subps0[newname]        

        for plock in ps[pname]:
          if plock not in subps:
            subps.append(plock)
            #print(pcontextname, pname, sub.contextname, newname, plock)
            changed = True
        if spread:
          for sub2 in nw:
            if sub2 is sub: continue
            sub2ps0 = matchsocks[sub2] if mode == "socket" else matchplugs[sub2]
            if newname not in sub2ps0: sub2ps0[newname] = []
            sub2ps = sub2ps0[newname]        
            for plock in ps[pname]:
              if plock not in sub2ps:
                #print(pcontextname, pname, sub2.contextname, newname, plock)
                sub2ps.append(plock)
                changed = True

        if changed: network_updated2[nwindex].add(newname)  
        
    network_updated_s = network_updated2_s
    network_updated_p = network_updated2_p

    #resolve evcontexts (not evexc)
    for snr,sub in enumerate(subcontexts):
      if sub not in evcontexts: continue
      pname, evname = sub.contextname[:-1], sub.contextname[-1]
      if evname == "evexc": continue
      if len(pname) == 1: pname = pname[0]
      pcontext = contextdict[pname]
      for s in pcontext.sockets:
        if not isinstance(s, tuple): continue
        if s[0] != evname: continue
        s2 = s[1:]
        if len(s2) == 1: s2 = s2[0]
        imp = (pcontext, s, s2, False)
        if imp not in sub.socket_imports:
          sub.socket_imports.append(imp)
          anychanged = True
      for p in pcontext.plugins:
        if not isinstance(p, tuple): continue
        if p[0] != evname: continue
        p2 = p[1:]
        if len(p2) == 1: p2 = p2[0]
        imp = (pcontext, p, p2, False)
        if imp not in sub.plugin_imports:
          sub.plugin_imports.append(imp)
          anychanged = True
    evchanged = resolve_evmap(subcontexts, evconmap_fwd)
    if evchanged: anychanged = True

  connections = {}
  all_connections  = set()  
  for snr,sub in enumerate(subcontexts):
    sname = sub.contextname
    if sname[-1].startswith("<<con"):
      if not hasattr(sub, "connect"): continue
      connect = sub.connect
      if not hasattr(connect, "parent"): continue
      cont = connect.parentcontext
      pos = None
      for beenr, bee0 in enumerate(connect.parent.bees):
        beename, bee = bee0
        if bee is connect: 
          pos = beenr
          break
      assert pos is not None    
      if cont not in subcontexts: continue
      if cont not in connections: connections[cont] = []
      connections[cont].append((pos, sub))
      all_connections.add(sub)
    
  #match sockets and plugins
  for snr,sub in enumerate(subcontexts):
    if sub in all_connections: continue
    if sub in connections:
      connections[sub].sort(key = lambda v: v[0])
      for pos, con in connections[sub]:
        if con in in_network:
          con.sockets = dict([(k,v) for k,v in matchsocks[con].items() if len(v)])
          con.plugins = dict([(k,v) for k,v in matchplugs[con].items() if len(v)])
        matchreport0("CONTEXT", con.contextname, sub.contextname)
        contextmatch(
         con, con.contextname,  
         con.sockets, con.plugins,
         con.socket_imports, con.plugin_imports, 
         con.socket, con.plugin,
        )
      
    
    sname = sub.contextname
    #if sname[-1].startswith("<<con"):
    #  print(sname)
    matchreport0("CONTEXT", sname)
    
    cnetwork = {}
    if sub in in_network:
      cnetwork = networks[in_network[sub]]
  
    #print(snr)
    #print(matchsocks[sub])
    #print(matchplugs[sub])
    sub.sockets = dict([(k,v) for k,v in matchsocks[sub].items() if len(v)])
    sub.plugins = dict([(k,v) for k,v in matchplugs[sub].items() if len(v)])
    contextmatch(
     sub, sub.contextname,  
     sub.sockets, sub.plugins,
     sub.socket_imports, sub.plugin_imports, 
     sub.socket, sub.plugin,
    )
  
def build_network(network, subcontexts, subcontextnames, parentdict):
  from .context import context as class_context
  change = True
  while change:
    change = False
    network2 = {}
    for subcontextname, subcontext in zip(subcontextnames, subcontexts):
      if subcontextname in network: continue
      if subcontextname not in parentdict: continue
      if parentdict[subcontextname] not in network: continue
      if not isinstance(subcontext, class_context): continue
      if subcontext.import_all_from_parent == False: continue
      #print(subcontextname)
      network2[subcontextname] = subcontext
      change = True     
    network.update(network2)
    
def resolve_evmap(subcontexts, evconmap_fwd):
  changed = False
  for sub in subcontexts:
    for evsrc, tar, tarname, evtar in evconmap_fwd[sub]:
      for sock in sub.sockets:
        if not isinstance(sock, tuple): continue
        if not sock[0] == evsrc: continue
        tarsock = (evtar,) + sock[1:]
        for socket in sub.sockets[sock]:
          new = tar.socket(tarsock, socket)
          if new: changed = True
      for imp in sub.socket_imports:          
        contextinstance, name, newname, optional = imp
        assert name is not None, (contextinstance, name, newname, optional) ##obsolete?
        if not isinstance(newname, tuple): continue
        if not newname[0] == evsrc: continue          
        tarname = (evsrc,) + newname[1:]
        new = tar.import_socket(contextinstance, name, tarname, optional)
        if new: changed = True

      for plug in sub.plugins:
        if not isinstance(plug, tuple): continue
        if not plug[0] == evsrc: continue
        tarplug = (evtar,) + plug[1:]
        for plugin in sub.plugins[plug]:
          new = tar.plugin(tarplug, plugin)
          if new: changed = True

      for imp in sub.plugin_imports:
        contextinstance, name, newname, optional = imp
        assert name is not None, (contextinstance, name, newname, optional) ##obsolete?
        if not isinstance(newname, tuple): continue
        if not newname[0] == evsrc: continue
        tarname = (evsrc,) + newname[1:]
        new = tar.import_plugin(contextinstance, name, tarname, optional)
        if new: changed = True
  return changed
