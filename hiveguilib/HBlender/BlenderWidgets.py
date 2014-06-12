import bpy
import weakref
from .BlenderWidgetManager import define_widget, define_widget_button
from . import level


class BlenderDummyWidget:
    def __init__(self, parent, drawfunc):
        self.parent = weakref.ref(parent)
        self.drawfunc = drawfunc

    def __getattr__(self, attr):
        raise NotImplementedError(attr)

    def draw(self, context, layout):
        self.drawfunc(context, layout)


class BlenderWrapWidget:
    def __init__(self, parent):
        self.parent = weakref.ref(parent)

    def __getattr__(self, attr):
        raise NotImplementedError(attr)


class BlenderEmptyWidget:
    def __init__(self, parent):
        self.parent = weakref.ref(parent)

    def show(self):
        pass

    def hide(self):
        pass

    def setParent(self, widget):
        self.parent = weakref.ref(widget)

    def __getattr__(self, attr):
        raise NotImplementedError(attr)


class BlenderWidget:
    def __init__(self, parent):
        if parent is None:
            self.parent = lambda: None
        else:
            self.parent = weakref.ref(parent)
        self._visible = True

    def draw(self, context, layout):
        if not self._visible:
            return
        if self.advanced:
            if not level.minlevel(context, 2):
                return
        self.draw2(context, layout)

    def draw2(self, context, layout):
        raise NotImplementedError

    def show(self):
        self._visible = True

    def hide(self):
        self._visible = False

    def setParent(self, parent):
        if parent is None:
            self.parent = lambda: None
        else:
            self.parent = weakref.ref(parent)


class BlenderLayoutWidget(BlenderWidget):
    def __init__(self, parent, name=None, buttons=[], advanced=False):
        self.name = name
        self.children = []
        self.pre_buttons = [w for w in buttons if w.layout == "before"]
        self.post_buttons = [w for w in buttons if w.layout == "after"]
        self.advanced = advanced
        BlenderWidget.__init__(self, parent)

    def __getattr__(self, attr):
        raise NotImplementedError(attr)

    def _is_visible(self):
        visible = False
        for w in self.pre_buttons + self.children + self.post_buttons:
            if not w._visible: continue
            if isinstance(w, BlenderLayoutWidget):
                if not w._is_visible(): continue
            visible = True
            break
        return visible

    def draw2(self, context, layout):
        if self.name is not None:
            layout = layout.row()
            layout.label("LAYOUT_WIDGET" + str(self.name))
        if not self.children and not self.pre_buttons and not self.post_buttons: return
        if not self._is_visible(): return
        layout = layout.box()
        """
        #TODO: column/row layout (__init__ option, determined from the spyderform) 
        """
        for but in self.pre_buttons:
            but.draw(context, layout)
        for child in self.children:
            child.draw(context, layout)
        for but in self.post_buttons:
            but.draw(context, layout)


class BlenderPlaceholderWidget(BlenderWidget):
    def __init__(self, parent, name, typ, advanced=False):
        self.name = name
        self.typ = typ
        self.value = None
        self.advanced = advanced
        BlenderWidget.__init__(self, parent)

    def listen(self, callback): pass

    def set(self, value): self.value = value

    def get(self): return self.value

    def draw2(self, context, layout):
        txt = "Placeholder: name '%s', type '%s', value '%s'" % (self.name, self.typ, self.value)
        layout.label("PLACEHOLDER" + txt)


class BlenderLabelWidget(BlenderWidget):
    def __init__(self, parent, text, advanced=False):
        self.text = text
        self.advanced = advanced
        BlenderWidget.__init__(self, parent)

    def draw2(self, context, layout):
        layout.label("LABEL_WIDGET" + self.text)


class BlenderButtonWidget(BlenderWidget):
    def __init__(self, parent, txt, layout=None, advanced=False):
        self.txt = txt
        self.layout = layout  # "before" or "after"
        self.widget_id = define_widget_button(self.press)
        self.widget = self  # for spyder.formtools.arraymanager_dynamic
        self._listeners = []
        self.advanced = advanced
        BlenderWidget.__init__(self, parent)

    def listen(self, callback):
        self._listeners.append(callback)

    def unlisten(self, callback):
        self._listeners.remove(callback)

    def press(self):
        for callback in self._listeners:
            callback()

    def draw2(self, context, layout):
        layout.operator(self.widget_id, self.txt)


class BlenderIntWidget(BlenderWidget):
    def __init__(self, parent, name, advanced=False):
        self.name = name
        self.value = None
        self.widget_id = define_widget(bpy.props.IntProperty, "intprop", self.get, self.set)
        self._listeners = []
        self.advanced = advanced
        BlenderWidget.__init__(self, parent)

    def listen(self, callback):
        self._listeners.append(callback)

    def unlisten(self, callback):
        self._listeners.remove(callback)

    def block(self):
        self._blockedcount += 1

    def unblock(self):
        self._blockedcount -= 1
        if self._blockedcount < 0: self._blockedcount = 0

    def set(self, value):
        self.value = value
        for callback in self._listeners: callback(self.value)

    def get(self):
        if self.value is None: return 0
        return self.value

    def draw2(self, context, layout):
        layout.prop(context.scene, self.widget_id, text=str(self.name))


class BlenderFloatWidget(BlenderWidget):
    def __init__(self, parent, name, advanced=False):
        self.name = name
        self.value = None
        self.widget_id = define_widget(bpy.props.FloatProperty, "floatprop", self.get, self.set)
        self._listeners = []
        self.advanced = advanced
        BlenderWidget.__init__(self, parent)

    def listen(self, callback):
        self._listeners.append(callback)

    def unlisten(self, callback):
        self._listeners.remove(callback)

    def block(self):
        self._blockedcount += 1

    def unblock(self):
        self._blockedcount -= 1
        if self._blockedcount < 0: self._blockedcount = 0

    def set(self, value):
        self.value = value
        for callback in self._listeners: callback(self.value)

    def get(self):
        if self.value is None: return 0.0
        return self.value

    def draw2(self, context, layout):
        layout.prop(context.scene, self.widget_id, text=str(self.name))


class BlenderStringWidget(BlenderWidget):
    def __init__(self, parent, name, advanced=False):
        self.name = name
        self.value = None
        self.widget_id = define_widget(bpy.props.StringProperty, "stringprop", self.get, self.set)
        self._listeners = []
        self.advanced = advanced
        BlenderWidget.__init__(self, parent)

    def listen(self, callback):
        self._listeners.append(callback)

    def unlisten(self, callback):
        self._listeners.remove(callback)

    def block(self):
        self._blockedcount += 1

    def unblock(self):
        self._blockedcount -= 1
        if self._blockedcount < 0: self._blockedcount = 0

    def set(self, value):
        self.value = value
        for callback in self._listeners: callback(self.value)

    def get(self):
        if self.value is None: return ""
        return str(self.value)

    def draw2(self, context, layout):
        layout.prop(context.scene, self.widget_id, text=str(self.name))


class BlenderBoolWidget(BlenderWidget):
    def __init__(self, parent, name, advanced=False):
        self.name = name
        self.value = None
        self.widget_id = define_widget(bpy.props.BoolProperty, "boolprop", self.get, self.set)
        self._listeners = []
        self.advanced = advanced
        BlenderWidget.__init__(self, parent)

    def listen(self, callback):
        self._listeners.append(callback)

    def unlisten(self, callback):
        self._listeners.remove(callback)

    def block(self):
        self._blockedcount += 1

    def unblock(self):
        self._blockedcount -= 1
        if self._blockedcount < 0: self._blockedcount = 0

    def set(self, value):
        self.value = value
        for callback in self._listeners: callback(self.value)

    def get(self):
        if self.value is None: return False
        return self.value

    def draw2(self, context, layout):
        layout.prop(context.scene, self.widget_id, text=str(self.name))


class BlenderOptionWidget(BlenderWidget):
    """
    Defines an multiple-choice string widget
    """

    def __init__(self, parent, name, options, option_names=None, option_descriptions=None, advanced=False,
                 advanced_options=None):
        self.name = name
        self.value = None  # string!
        if option_names is not None: assert len(option_names) == len(options)
        if option_descriptions is not None: assert len(option_descriptions) == len(options)
        self.options = [str(o) for o in options]
        self.option_names = option_names
        self.option_descriptions = option_descriptions

        def get_items2(dummy, dummy2):
            return self.get_items()

        self.widget_id = define_widget(bpy.props.EnumProperty,
                                       "enumprop", self.get_index, self.set_index, items=get_items2,
                                       name=str(self.name))
        self._listeners = []
        self.advanced = advanced
        if self.advanced: assert advanced_options is None
        self.advanced_options = None
        if advanced_options is not None:
            self.advanced_options = [str(o) for o in advanced_options]
            for o in self.advanced_options: assert o in self.options
        BlenderWidget.__init__(self, parent)

    def listen(self, callback):
        self._listeners.append(callback)

    def unlisten(self, callback):
        self._listeners.remove(callback)

    def block(self):
        self._blockedcount += 1

    def unblock(self):
        self._blockedcount -= 1
        if self._blockedcount < 0: self._blockedcount = 0

    def set(self, value):
        assert value is None or str(value) in self.options, (value, self.options)
        if value is None:
            self.value = None
        else:
            self.value = str(value)
        for callback in self._listeners: callback(self.value)

    def get(self):
        return self.value

    def get_index(self):
        if self.value is None: return 0
        return self.options.index(self.value) + 1

    def set_index(self, index):
        if index == 0:
            self.value = None
        else:
            self.value = self.options[index - 1]
        for callback in self._listeners: callback(self.value)

    def get_items(self):
        items = [("<empty>", "", "Value is not defined", 0)]
        op = self.options
        opn = self.option_names
        if opn is None: opn = op
        opd = self.option_descriptions
        if opd is None: opd = opn
        opnr = range(1, len(op) + 1)
        items2 = list(zip(op, opn, opd, opnr))
        if self.advanced_options is not None:
            if not level.minlevel(bpy.context, 2):
                items2 = [i for i in items2 if i[0] not in self.advanced_options or i[0] == self.value]
        return items + items2

    def draw2(self, context, layout):
        layout.prop(context.scene, self.widget_id, text=str(self.name))
        