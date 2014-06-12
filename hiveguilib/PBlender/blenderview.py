from collections import OrderedDict
from functools import partial
import weakref
import sys
from spyder import validvar2
import Spyder
from ..HBlender.BlenderWidgets import *
from ..HBlender.BlenderTextWidget import BlenderTextWidget

reserved = (
    "type", "value", "default", "typename", "members",
    "arraycount", "default_expr", "is_default"
)


def get_formtype(form, name):
    if form.arraycount > 0: return None, None
    if form.get_membernames(): return None, None

    if form.typename is None:
        typnam = "None" + "Array" * form.arraycount
    else:
        typnam = form.typename + "Array" * form.arraycount

    try:
        typ = getattr(Spyder, form.typename)
    except AttributeError:
        typ = Spyder.String
    formtype = "text"
    formsubtype = None
    if issubclass(typ, Spyder.File):
        if form.arraycount > 0:
            raise TypeError("Cannot generate Blender layout for \"%s\"(%s): array of files" % (name, typnam))
        if not hasattr(form, "file"):
            raise TypeError(
                "Cannot generate Blender layout for \"%s\"(%s): a file type (file attribute) must be specified" % (
                name, typnam))
        if hasattr(form, "options"):
            raise TypeError(
                "Cannot generate Blender layout for \"%s\"(%s): file elements cannot have options" % (name, typnam))
        formtype = "file"
    elif issubclass(typ, Spyder.Integer) or issubclass(typ, Spyder.Float):
        formtype = "spin"
        if issubclass(typ, Spyder.Integer):
            formsubtype = "int"
        elif issubclass(typ, Spyder.Float):
            formsubtype = "float"

    elif issubclass(typ, Spyder.Bool):
        formtype = "checkbox"

    if hasattr(form, "options"):
        assert formtype != "file"
        formtype = "option"
        options = form.options
        optiontitles = options
        if hasattr(form, "optiontitles"):
            optiontitles = form.optiontitles
            assert len(options) == len(optiontitles), (n, len(options), len(optiontitles))

    if hasattr(form, "type"):
        if form.type not in ("required", "none"):
            formtype = form.type
            formsubtype = None
            if hasattr(form, "subtype"):
                formsubtype = form.subtype
            if formsubtype is None:
                if issubclass(typ, Spyder.Integer):
                    formsubtype = "int"
                elif issubclass(typ, Spyder.Float):
                    formsubtype = "float"

    return (formtype, formsubtype)


class blenderview_primary:
    def __init__(self, value_callback, set_callback, listen_callback, widget):
        self.widget = widget
        self._listen_callback = listen_callback
        self._value_callback = value_callback
        self.set = set_callback
        self._listeners = []
        self._listen_handler = None
        self._blockedcount = 0

    def _listener(self, *args):
        # print("LISTEN!", self, self._blockedcount, self._value_callback())
        if self._blockedcount: return
        for callback in self._listeners:
            callback(*args)

    def listen(self, callback):
        if self._listen_handler is None:
            self._listen_handler = self._listen_callback(self._listener)
        self._listeners.append(callback)

    def unlisten(self, callback):
        self._listeners.remove(callback)

    def block(self):
        self._blockedcount += 1

    def unblock(self):
        self._blockedcount -= 1
        if self._blockedcount < 0: self._blockedcount = 0

    def __getattr__(self, attr):
        if attr != "value": raise AttributeError(attr)
        ret = self._value_callback()
        return ret

    def __str__(self):
        return str(self._value_callback())


def find_buttons(form):
    if form is None or "_othertokens" not in form._props: return []
    tokens = form._props["_othertokens"]
    ret = []
    for token, args in tokens:
        if token == "button":
            txt, layout = args
            assert layout in ("before", "after"), layout
            w = BlenderButtonWidget(None, txt, layout)
            ret.append(w)
    return ret


class blenderview:
    def __init__(self, obj, form=None, parent=None, name=None, value=None):
        import spyder, Spyder
        from Spyder import Object
        from spyder.formtools import arraymanager_dynamic

        if isinstance(obj, Object):
            form = obj._form()
        elif isinstance(obj, spyder.core.spyderform):
            form = obj
        else:
            ok = False
            try:
                if issubclass(obj, Object):
                    form = obj._form()
                    ok = True
            except TypeError:
                pass
            if not ok: raise TypeError(obj)

        if parent is None:
            arraymanager_dynamic.add_buttons(form)

        if hasattr(form, "value"):
            defaultvalue = form.value
        elif value is not None:
            defaultvalue = value
        elif hasattr(form, "default"):
            defaultvalue = form.default
        else:
            defaultvalue = None

        self.buttons = find_buttons(form)
        self._getters = {}
        self._setters = {}
        self._name = name
        self._form = form
        self.typename = form.typename
        self.type = None
        self._parent = None
        if self.typename is not None and validvar2(self.typename):
            self.type = getattr(Spyder, self.typename + "Array" * form.arraycount)
        self._listen_callbacks = None
        pw = None
        if parent is not None: pw = parent.widget
        if parent is None or not len(self.buttons):
            self.widget = BlenderLayoutWidget(pw, self._name, self.buttons)
            for b in self.buttons: b.setParent(self.widget)
            widget = self.widget
        else:
            self._pwidget = BlenderLayoutWidget(pw, self._name, self.buttons)
            for b in self.buttons: b.setParent(self._pwidget)
            self.widget = BlenderLayoutWidget(self._pwidget, self._name, [])
            self._pwidget.children.append(self.widget)
            widget = self._pwidget
        if parent is not None:
            parent.widget.children.append(widget)
        self._setup(defaultvalue)

    def _value(self):
        if self._form.arraycount > 0:
            ret = []
            for n in range(self._form.length):
                v = self._getters.get(str(n), None)
                if v is not None: v = v.value
                ret.append(v)
        else:
            ret = {}
            for prop in self._properties:
                ret[prop] = self._getters[prop].value
        return ret

    def __str__(self):
        return str(self._value())

    def set(self, v):
        if self.type is None: raise AttributeError
        if isinstance(v, self.type):
            vv = v
        else:
            vv = self.type(v)
        for prop in self._properties:
            if self._form.arraycount > 0:
                try:
                    val = vv[int(prop)]
                except IndexError:
                    continue
            else:
                val = getattr(vv, prop)
            self._setters[prop](val)

    def _listener(self, dmmy):
        v = self._value()
        for l in self._listen_callbacks:
            l(v)

    def block(self):
        for prop in self._properties:
            self._getters[prop].block()

    def unblock(self):
        for prop in self._properties:
            self._getters[prop].unblock()

    def listen(self, callback):
        if self._listen_callbacks is None:
            self._listen_callbacks = []
            for prop in self._properties:
                proplis = self._prop_listeners[prop]
                proplis(self._listener)
        self._listen_callbacks.append(callback)

    def unlisten(self, callback):
        self._listen_callbacks.remove(callback)

    def _setup(self, defaultvalue):
        self._prop_listeners = {}
        toplevel = False
        self._properties = OrderedDict()
        form = self._form
        formnames = []
        subvalues = []
        getfunc = None
        if hasattr(form, "type") and form.type == "none": return
        if form is not None:
            if form.get_membernames() is not None:
                formnames = form.get_membernames()
                getfunc = partial(getattr, form)
                formvalues = []
                for formname in formnames:
                    mobj = None
                    if defaultvalue is not None:
                        mobj = getattr(defaultvalue, formname)
                    formvalues.append(mobj)
            elif form.arraycount > 0:
                if not hasattr(form, "length") or form.length is None: raise ValueError(form.typename)
                formnames = [str(v) for v in range(form.length)]
                formvalues = []
                for nr in range(form.length):
                    mobj = None
                    if defaultvalue is not None and len(defaultvalue) > nr:
                        mobj = defaultvalue[nr]
                    formvalues.append(mobj)
                getfunc = lambda v: form.__getitem__(int(v))
            else:
                raise ValueError(self._name)
        self._subformfunc = getfunc
        for formname, formvalue in zip(formnames, formvalues):
            mform = getfunc(formname)
            if hasattr(mform, "type") and mform.type is None: continue

            name = formname
            if name is not None and name.endswith("_"):
                for r in reserved:
                    if name == r + "_":
                        name = r
                        break
            if hasattr(mform, "name"): name = mform.name

            formtype, formsubtype = get_formtype(mform, formname)
            if formtype is not None:
                if hasattr(mform, "value"):
                    formdefault = mform.value
                elif formvalue is not None:
                    formdefault = formvalue
                elif hasattr(mform, "default"):
                    formdefault = mform.default
                else:
                    formdefault = None
                self._properties[formname] = (name, formtype, formsubtype, formdefault)
            else:
                view = blenderview(mform, parent=self, name=name, value=formvalue)
                self._properties[formname] = view

        for prop in self._properties:
            v = self._properties[prop]
            mform = self._subformfunc(prop)

            if isinstance(v, blenderview):
                self._getters[prop] = v
                self._setters[prop] = v.set
                self._prop_listeners[prop] = v.listen
                continue
            advanced = getattr(mform, "advanced", False)
            name, formtype, formsubtype, formdefault = v
            if formtype == "spin" and formsubtype == "int":
                widget = BlenderIntWidget(self.widget, name, advanced=advanced)
            elif formtype == "spin" and formsubtype == "float":
                widget = BlenderFloatWidget(self.widget, name, advanced=advanced)
            elif formtype == "checkbox":
                widget = BlenderBoolWidget(self.widget, name, advanced=advanced)
            elif formtype in ('text', 'password', 'type', 'expression'):
                widget = BlenderStringWidget(self.widget, name, advanced=advanced)
            elif formtype in ('option', 'radio'):
                options = mform.options
                optiontitles = None
                if hasattr(mform, "optiontitles"):
                    optiontitles = mform.optiontitles
                    assert len(options) == len(optiontitles), (n, len(options), len(optiontitles))
                advanced_options = getattr(mform, "advanced_options", None)
                widget = BlenderOptionWidget(
                    self.widget,
                    name, options, optiontitles,
                    advanced=advanced, advanced_options=advanced_options
                )
            elif formtype in ('textarea', 'pythoncode'):
                widget = BlenderTextWidget(self.widget, name, advanced=advanced)
            elif formtype in ('file', 'object'):
                widget = BlenderPlaceholderWidget(self.widget, name, formtype, advanced=advanced)
            else:
                raise Exception("Form element '%s': Not implemented" % str(v))

            if formdefault is not None:
                widget.set(formdefault)
            getprop, setprop, proplis = widget.get, widget.set, widget.listen
            viewbuttons = find_buttons(mform)
            widget2 = widget
            if len(viewbuttons):
                widget2 = BlenderLayoutWidget(self.widget, name, viewbuttons)
                for b in viewbuttons: b.setParent(widget2)
                widget2.children.append(widget)
            self.widget.children.append(widget2)
            view = blenderview_primary(getprop, setprop, proplis, widget)
            view.buttons = viewbuttons
            self._properties[prop] = view
            self._getters[prop] = view
            self._setters[prop] = setprop
            self._prop_listeners[prop] = proplis

    def __getitem__(self, key):
        assert isinstance(key, int)
        assert key >= 0
        assert self._form.arraycount > 0
        return self._getters[str(key)]

    def __getattr__(self, attr):
        if attr == "value": return self._value()
        try:
            return self._getters[attr]
        except KeyError:
            raise AttributeError(attr)

    def __setattr__(self, attr, value):
        if attr.startswith("_") or attr in ("type", "typename", "buttons", "widget"):
            return object.__setattr__(self, attr, value)
        try:
            return self._setters[attr](value)
        except KeyError:
            raise AttributeError(attr)
  