from __future__ import print_function
from . import context
from .context import report, namesortfunc


class evcontext(context):
    priority = 1

    def parent_do_export(self):
        from . import _contexts as contexts, get_curr_contextname, _all_connections

        report("PARENT-DO-EXPORT", self.contextname)

        # print("PARENT-EXPORT-EV", self.contextname)
        #print(self.plugins.keys(), [p[2] for p in self.plugin_imports])
        #print(self.sockets.keys(), [p[2] for p in self.socket_imports])
        #print("")

        parent = None
        myname = self.contextname
        while True:
            myname = myname[:-1]
            if not len(myname): break
            if myname in contexts:
                parent = contexts[myname]
                break
        if not parent: raise Exception

        for sock in sorted(self.sockets.keys(), key=namesortfunc):
            nsock = sock if isinstance(sock, tuple) else (sock,)
            nsock = (self._evcontextname,) + nsock
            #print("NSOCK", nsock)
            parent.import_socket(self, sock, nsock)
        for plug in sorted(self.plugins.keys(), key=namesortfunc):
            nplug = plug if isinstance(plug, tuple) else (plug,)
            nplug = (self._evcontextname,) + nplug
            parent.import_plugin(self, plug, nplug)

        for sock in self.socket_imports:
            if sock[0] is parent: continue
            #nsock = sock[2] if isinstance(sock[2], tuple) else (sock[2],)
            nsock = (sock[2],)
            nsock = (self._evcontextname,) + nsock
            s = (self, sock[2], nsock, sock[3])
            if s in parent.socket_imports: continue
            parent.socket_imports.append(s)

        for plug in self.plugin_imports:
            if plug[0] is parent: continue
            #nplug = plug[2] if isinstance(plug[2], tuple) else (plug[2],)
            nplug = (plug[2],)
            nplug = (self._evcontextname,) + nplug
            p = (self, plug[2], nplug, plug[3])
            if p in parent.plugin_imports: continue
            #print("NPLUG", nplug, parent.contexts[-1].contextname)
            parent.plugin_imports.append(p)

    def parent_do_import(self):
        report("PARENT-DO-IMPORT", self.contextname)
        from . import _contexts as contexts, get_curr_contextname, _all_connections

        parent = None
        myname = self.contextname
        while True:
            myname = myname[:-1]
            if not len(myname): break
            if myname in contexts:
                parent = contexts[myname]
                break
        if not parent: raise Exception

        parent2 = parent
        parent_old = parent

        # print("PARENT-IMPORT-EV", self.contextname, parent_old.contextname)
        #print(list(parent.plugins.keys()), [p[2] for p in parent.plugin_imports])
        #print(list(parent.sockets.keys()), [p[2] for p in parent.socket_imports])
        #print("")

        for sock in sorted(parent.sockets.keys(), key=namesortfunc):
            if not isinstance(sock, tuple): continue
            if sock[0] != self._evcontextname: continue
            newsock = sock[1:]
            if len(newsock) == 1 and isinstance(newsock[0], str):
                newsock = newsock[0]
            self.import_socket(parent2, sock, newsock)

        for plug in sorted(parent.plugins.keys(), key=namesortfunc):
            if not isinstance(plug, tuple): continue
            if plug[0] != self._evcontextname: continue
            newplug = plug[1:]
            if len(newplug) == 1 and isinstance(newplug[0], str):
                newplug = newplug[0]
            self.import_plugin(parent2, plug, newplug)

        for sock in parent.socket_imports:
            if sock[0] is self: continue
            if not isinstance(sock[2], tuple): continue
            if sock[2][0] != self._evcontextname: continue
            newsock = sock[2][1:]
            if len(newsock) == 1 and isinstance(newsock[0], str):
                newsock = newsock[0]
            s = (parent2, sock[2], newsock, sock[3])
            #print("NNSOCK", sock[2])
            if s not in self.socket_imports:
                self.socket_imports.append(s)

        for plug in parent.plugin_imports:
            if plug[0] is self: continue
            if not isinstance(plug[2], tuple): continue
            if plug[2][0] != self._evcontextname: continue
            newplug = plug[2][1:]
            if len(newplug) == 1 and isinstance(newplug[0], str):
                newplug = newplug[0]
            p = (parent2, plug[2], newplug, plug[3])
            if p not in self.plugin_imports:
                self.plugin_imports.append(p)


class evincontext(evcontext): pass


class evoutcontext(evcontext): pass


class evexccontext(evcontext):
    priority = -1
    # pass


class evsubcontext:
    def __init__(self, contextclass, contextname, getparent):
        self._contextclass = contextclass
        self._getparent = getparent
        self._contextname = contextname

    def __place__(self):
        pass

    def place(self):
        import libcontext

        from . import push, pop
        from . import new_contextname

        self._contextname = new_contextname(self._contextname)
        self.context = self._contextclass(self._contextname)
        self.context._evcontextname = self._contextname
        parent = self._getparent()
        push(self._contextname)
        self.__place__()
        pop()

    def close(self):
        self.context.close()

