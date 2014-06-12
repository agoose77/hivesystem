import weakref

from .anyQt.QtGui import QCompleter


def get_typestrings0(type_):
    if isinstance(type_, str):
        return [type_]
    elif isinstance(type_, tuple):
        ret = [[], [], []]
        for t in type_:
            if isinstance(t, tuple):
                rr1, rr2, rr3 = get_typestrings0(t)
                ret[0] += rr1
                ret[1] += rr2
                ret[2] += rr3
            elif isinstance(t, str):
                ret[0].append(str(t))
                ret[1].append('"' + str(t) + '"')
                ret[2].append("'" + str(t) + "'")
            else:
                raise Exception(t)
        return ret[0], ret[1], ret[2]
    else:
        raise Exception(type_)


def get_typestrings(type_):
    r = get_typestrings0(type_)
    if isinstance(r, list):
        return r
    elif isinstance(r, tuple):
        assert len(r) == 3
        s = []
        for sep in ",", ", ":
            for rr in r:
                s.append(sep.join(rr))
        ret = []
        for parenth in True, False:
            s0 = "(" if parenth else ""
            s1 = ")" if parenth else ""
            for ss in s:
                assert isinstance(ss, str), ss
                ret.append(s0 + ss + s1)
        return ret
    else:
        raise Exception(r)


class TypeCompleter(object):
    def __init__(self):
        self.widgets = weakref.WeakValueDictionary()  # use WeakSet when 2.6 compat is dropped
        self.completer = None

    def set_typelist(self, typelist):
        self.typelist = typelist
        tl = []
        for t in self.typelist:
            tt = get_typestrings(t)
            tl += tt
        self.typestrings = tl
        self.completer = QCompleter(self.typestrings)
        for widget in self.widgets.values():
            widget.setCompleter(self.completer)

    def add_completers(self, v, form, path=None):
        if path is None:
            ppath = ()
        else:
            ppath = tuple(path)
        if form.arraycount > 0:
            for n in range(form.length):
                ppath2 = ppath + (n,)
                try:
                    f = form[n]
                    mv = v[n]
                except (KeyError, IndexError, AttributeError, TypeError) as exc:
                    raise type(exc)(*exc.args + (ppath2,))
                self.add_completers(mv, f, ppath2)
            return
        for pname, f in form._members.items():
            ppath2 = ppath + (pname,)
            if hasattr(f, "type") and f.type == "type" or \
                            hasattr(f, "typeinfo") and f.typeinfo == "type":
                try:
                    widget = getattr(v, pname).widget
                except AttributeError as exc:
                    raise type(exc)(*exc.args + (ppath2,))
                self.widgets[id(widget)] = widget
                if self.completer:
                    widget.setCompleter(self.completer)
            elif hasattr(f, "_members") and f._members is not None:
                try:
                    mv = getattr(v, pname)
                except AttributeError as exc:
                    raise type(exc)(*exc.args + (ppath2,))
                self.add_completers(mv, f, ppath2)

    def widgetmodifier(self, mode, parwidget, controller):
        if mode == "new":
            v = controller._view()
            form = controller._form
            self.add_completers(v, form)


        elif mode == "delete":
            return
        else:
            raise Exception
