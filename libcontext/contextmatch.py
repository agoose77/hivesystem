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
        if newname not in newsockets:
            newsockets[newname] = []

        newsockets[newname].append(s)

    for nwname in newsockets:
        currsockets = []
        for contextinstance, name, newname, optional in newsockets[nwname]:
            if name is not None:
                currsockets0 = retrieve_sockets(contextinstance, name)
                if currsockets0 is None:
                    if not optional:
                        raise Exception("%s does not contain a socket '%s'" % (contextinstance.contextname, name))
                else:
                    currsockets += currsockets0
            else:
                socketfunc(newname, None)

        currsockets0 = []
        for c in currsockets:
            if c not in currsockets0:
                currsockets0.append(c)

        currsockets = currsockets0

        currsockets.sort(key=namesortfunc2)
        for cname, s in currsockets:
            if contextinstance is not context and s not in sockets_original:
                import_origins_sockets[s] = contextinstance

            if newname in context.sockets and s in context.sockets[newname]:
                continue

            socketfunc(newname, s)


def import_plugins(context, plugin_imports, socket_imports, plugins_original, import_origins_plugins, pluginfunc):
    newplugins = {}
    for plugin in plugin_imports:
        newname = plugin[2]
        if newname not in newplugins:
            newplugins[newname] = []
        newplugins[newname].append(plugin)

    count = 1
    for nwname in newplugins:
        count += 1
        currplugins = []
        for contextinstance, name, newname, optional in newplugins[nwname]:
            if name is not None:
                # report("!", count, name, contextinstance.contextname)
                currplugins0 = retrieve_plugins(contextinstance, name)
                #report("!!")
                if currplugins0 is None:
                    if not optional:
                        report(
                            [(a[0].contextname,) + a[1:] for a in plugin_imports],
                            [(a[0].contextname,) + a[1:] for a in socket_imports],
                        )
                        raise Exception("%s does not contain a plugin '%s'" % (contextinstance.contextname, name))
                else:
                    currplugins += currplugins0
            else:
                pluginfunc(newname, None)

        currplugins = list(set(currplugins))
        currplugins.sort(key=namesortfunc2)

        for cname, plugin in currplugins:
            if contextinstance is not context and plugin not in plugins_original:
                import_origins_plugins[plugin] = contextinstance

            if newname in context.plugins and plugin in context.plugins[newname]:
                continue
            pluginfunc(newname, plugin)


def contextmatch(context, contextname, sockets, plugins, socket_imports, plugin_imports, socketfunc, pluginfunc):
    from . import _all_connections

    import_origins_plugins = {}
    import_origins_sockets = {}
    plugins_original0 = [plugins[p] for p in sorted(plugins, key=namesortfunc)]
    plugins_original = []

    for plugin in plugins_original0:
        plugins_original += plugin

    import_plugins(context, plugin_imports, socket_imports, plugins_original, import_origins_plugins, pluginfunc)

    sockets_original0 = [sockets[p] for p in sorted(sockets, key=namesortfunc)]
    sockets_original = []

    for socket in sockets_original0:
        sockets_original += socket

    import_sockets(context, socket_imports, plugin_imports, sockets_original, import_origins_sockets, socketfunc)

    filled_sockets = set()
    plugin_names = sorted(plugins.keys(), key=namesortfunc)
    socket_names = sorted(sockets.keys(), key=namesortfunc)
    
    for name in plugin_names:
        plugins_ = sorted(plugins[name], key=_plugids.__getitem__)

        for plugin in plugins_:
            if name not in sockets and plugin not in import_origins_plugins and plugin is not None:
                try:
                    plugin.unfilled()

                except Exception as e:
                    raise type(e)(*(e.args + (contextname, name)))

                continue

            filled_sockets.add(name)
            try:
                found_sockets = []
                if name in socket_names:
                    found_sockets += sockets[name]

                if found_sockets:
                    for socket in found_sockets:
                        if socket is None:
                            continue

                        if plugin in import_origins_plugins:
                            if plugin is None:
                                continue

                        if (socket, plugin) in _all_connections:
                            continue

                        _all_connections.add((socket, plugin))

                        try:
                            socket_context_name = socket.function.im_self.workerinstance._context.contextname
                            segment_name = socket.function.im_self.segmentname

                        except AttributeError:
                            pass
                        socket.fill(*plugin.args, **plugin.kargs)
                        plugin.fill(socket)

            except Exception as e:
                if python2:
                    e2 = type(e)(contextname, name, e.args)
                    do_raise(e2)

                else:
                    raise Exception(contextname, name)

    for name in socket_names:
        if name in filled_sockets:
            continue

        try:
            for socket in sockets[name]:
                if socket not in import_origins_sockets and socket is not None:
                    socket.unfilled()

        except Exception as e:
            from . import add_contextnames

            raise type(e)(*(e.args + (contextname, name)))
