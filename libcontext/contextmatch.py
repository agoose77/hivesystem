from .context import namesortfunc, namesortfunc2, retrieve_plugins, retrieve_sockets
from .context import _plugids
import sys
python2 = (sys.version_info[0] == 2)
python3 = (sys.version_info[0] == 3)

def do_raise(e):
  exec("raise type(e), e, sys.exc_info()[2]")


def import_sockets(context, socket_imports, plugin_imports, sockets_original, import_origins_sockets, socketfunc):
    newsockets = {}
    for s in socket_imports:
      newname = s[2]
      if newname not in newsockets: newsockets[newname] = []
      newsockets[newname].append(s)
    for nwname in newsockets:
      currsockets = []
      for contextinstance, name, newname, optional in newsockets[nwname]:
        if name != None:
          currsockets0 = retrieve_sockets(contextinstance, name)
          if currsockets0 is None:
           if not optional:
             raise Exception("%s does not contain a socket '%s'" % (contextinstance.contextname, name))
          else:
            currsockets += currsockets0
        else: socketfunc(newname, None)
      currsockets0 = []
      for c in currsockets: 
        if c not in currsockets0: currsockets0.append(c)
      currsockets = currsockets0

      currsockets.sort(key = namesortfunc2)
      for cname, s in currsockets:
        if contextinstance is not context and s not in sockets_original: import_origins_sockets[s] = contextinstance
        if newname in context.sockets and s in context.sockets[newname]: continue
        socketfunc(newname, s)         

def import_plugins(context, plugin_imports, socket_imports, plugins_original, import_origins_plugins, pluginfunc):
  newplugins = {}
  for p in plugin_imports:
    newname = p[2]
    if newname not in newplugins: newplugins[newname] = []
    newplugins[newname].append(p)
  count = 1
  for nwname in newplugins:       
    count += 1
    currplugins = []    
    for contextinstance, name, newname, optional in newplugins[nwname]:        
      if name != None:
        #report("!", count, name, contextinstance.contextname)
        currplugins0 = retrieve_plugins(contextinstance, name)
        #report("!!")
        if currplugins0 is None:
         if not optional:
           report(
             [(a[0].contextname,)+a[1:] for a in plugin_imports], 
             [(a[0].contextname,)+a[1:] for a in socket_imports],
           )
           raise Exception("%s does not contain a plugin '%s'" % (contextinstance.contextname, name))
        else:
          currplugins += currplugins0
      else: pluginfunc(newname, None)
    currplugins = list(set(currplugins))
    currplugins.sort(key = namesortfunc2)       
    for cname, p in currplugins:
      if contextinstance is not context and p not in plugins_original: import_origins_plugins[p] = contextinstance
      if newname in context.plugins and p in context.plugins[newname]: continue
      pluginfunc(newname, p)         


def contextmatch(
 context, contextname,
 sockets, plugins, 
 socket_imports, plugin_imports,
 socketfunc, pluginfunc,
):
    from . import _all_connections
    import_origins_plugins = {}
    import_origins_sockets = {}
    plugins_original0 = [plugins[p] for p in sorted(plugins,key=namesortfunc)]
    plugins_original = []
    for p in plugins_original0: plugins_original += p
    import_plugins(context, plugin_imports, socket_imports, plugins_original, import_origins_plugins, pluginfunc)   
    
    sockets_original0 = [sockets[p] for p in sorted(sockets,key=namesortfunc)]
    sockets_original = []
    for s in sockets_original0: sockets_original += s
    import_sockets(context, socket_imports, plugin_imports, sockets_original, import_origins_sockets, socketfunc)   

    filled_sockets = set()
    pluginnames = list(plugins.keys())
    pluginnames.sort(key=namesortfunc)
    socketnames = list(sockets.keys())
    socketnames.sort(key=namesortfunc)     
    for name in pluginnames:                       
      plugs = plugins[name]
      plugs.sort(key=lambda p: _plugids[p])
      for p in plugs:
        if name not in sockets \
         and p not in import_origins_plugins \
         and p != None:            
          try:
            p.unfilled()
          except Exception as e:
            raise type(e)(*(e.args + (contextname, name)))
          continue
        filled_sockets.add(name)
        try:      
          found_sockets = []
          if name in socketnames:
            found_sockets += sockets[name]
          if len(found_sockets):
            for s in found_sockets:
              if s == None: continue
              if p in import_origins_plugins: 
                if p == None: continue        
              if (s,p) in _all_connections:
                continue
              _all_connections.add((s,p))

              try:
                socketcontextname = s.function.im_self.workerinstance._context.contextname
                segmentname = s.function.im_self.segmentname
              except AttributeError:
                pass
              s.fill(*p.args, **p.kargs)
              p.fill(s)
        except Exception as e:               
          if python2: 
            e2 = type(e)(contextname, name, e.args)
            do_raise(e2)            
          else: raise Exception(contextname, name)
    for name in socketnames:
      if name in filled_sockets: continue
      try:
        for s in sockets[name]:             
          if s not in import_origins_sockets and s != None: 
            s.unfilled()
      except Exception as e:
        from . import add_contextnames
        raise type(e)(*(e.args + (contextname, name)))
