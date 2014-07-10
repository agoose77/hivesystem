from __future__ import print_function

import weakref
from functools import partial

from .. import PersistentIDManager


def _hide(widgets):
    for w in widgets: w.hide()


def _show(widgets):
    for w in widgets: w.show()


def control_visibility(widget):
    label = widget.parent().layout().labelForField(widget)
    widgets = [widget, label]
    return partial(_show, widgets), partial(_hide, widgets)


class AntennaFoldState(object):

    def __init__(self, parent):
        self._parent = weakref.ref(parent)
        self._widgets = {}
        self._submodels = {}
        self._values_to_set = []
        self._variables_to_set = []

        self._persisent_id_manager = PersistentIDManager()

    def p_expand(self, workerid, a):
        if a not in self._widgets[workerid]: return
        for on, off in self._widgets[workerid][a]:
            on()

    def gui_expands(self, persistent_id, a):
        workerid = self._persisent_id_manager.get_temporary_id(persistent_id)
        self._parent().gui_expands(workerid, a)

    def p_fold(self, workerid, a):
        if a not in self._widgets[workerid]: return
        for on, off in self._widgets[workerid][a]:
            off()

    def gui_folds(self, persistent_id, a):
        workerid = self._persisent_id_manager.get_temporary_id(persistent_id)
        self._parent().gui_folds(workerid, a)

    def gui_sets_value(self, persistent_id, a, value):
        workerid = self._persisent_id_manager.get_temporary_id(persistent_id)
        self._parent().gui_sets_value(workerid, a, value)

    def init_form(self, workerid, form):
        p = self._parent()
        state = p.states[workerid]
        if state is None: return
        for a in state:
            antenna = state[a]
            ele = getattr(form, a, None)
            if ele is None: continue
            name = getattr(ele, "name", a)
            ele.add_button("Expand %s" % name, "before")
            if antenna.foldable:
                ele.add_button("Fold %s" % name, "before")

    def init_widget(self, workerid, widget, controller):
        from spyder.qtform.anyQt.QtGui import QFormLayout

        p = self._parent()
        state = p.states[workerid]
        if state is None: return
        view = controller._view()
        model = controller._model()
        self._widgets[workerid] = {}
        self._submodels[workerid] = {}

        persistent_id = self._persisent_id_manager.create_persistent_id(workerid)

        for antenna_name in state:
            antenna = state[antenna_name]
            widgets = []
            ele = getattr(view, antenna_name, None)
            if ele is None: continue
            if not hasattr(ele, "widget"):
                raise Exception("Unfoldable: %s.%s has no associated widget in parameter tab" % (workerid, antenna_name))
            e = ele.widget
            classname = e.metaObject().className()
            if classname == "QLineEdit":
                show, hide = control_visibility(e)
                on, off = show, hide
            else:
                on, off = e.show, e.hide
            widgets.append((off, on))  # expand / fold

            # KLUDGE: Qt XML generator is pretty borked up... this will put the buttons in a better place
            newlayout = None
            pw = ele.buttons[0].widget.parent()
            if pw.objectName().startswith("_expw"):
                newlayout = pw.parent().layout().children()[0]

            if antenna.foldable:
                b = ele.buttons[1]  #Fold button
                b.listen(partial(self.gui_folds, persistent_id, antenna_name))
                if newlayout is not None:  ##KLUDGE
                    newlayout.addWidget(b.widget)
                on, off = b.widget.show, b.widget.hide
                widgets.append((on, off))  #expand / fold
            b = ele.buttons[0]  #Expand button
            b.listen(partial(self.gui_expands, persistent_id, antenna_name))
            if newlayout is not None:  ##KLUDGE
                newlayout.addWidget(b.widget)
            on, off = b.widget.show, b.widget.hide
            widgets.append((off, on))  #expand / fold
            self._widgets[workerid][antenna_name] = widgets

            submodel = getattr(model, antenna_name, None)
            self._submodels[workerid][antenna_name] = submodel
            submodel._listen(partial(self.gui_sets_value, persistent_id, antenna_name))

        currv = [v for v in self._values_to_set if v[0] == workerid]
        self._values_to_set = [v for v in self._values_to_set if v[0] != workerid]
        done = set()
        for wid, member, value in currv:
            done.add(member)
            self._submodels[workerid][member]._set(value)

        currv = [v for v in self._variables_to_set if v[0] == workerid]
        self._variables_to_set = [v for v in self._variables_to_set if v[0] != workerid]
        for wid, member in currv:
            if member in done: continue
            value = self._submodels[workerid][member]._get()
            if value is not None:
                self._parent().gui_sets_value(workerid, member, value)

    def remove_worker(self, workerid):
        self._widgets.pop(workerid)
        self._submodels.pop(workerid)

        self._persisent_id_manager.remove_with_temporary_id(workerid)

    def rename_worker(self, workerid, newid):
        w = self._widgets.pop(workerid)
        self._widgets[newid] = w
        s = self._submodels.pop(workerid)
        self._submodels[newid] = s

        self._persisent_id_manager.change_temporary_with_temporary_id(workerid, newid)

    def p_set_value(self, workerid, member, value):
        assert self._parent().states[workerid][member].is_folded == True, (workerid, member)
        init = self._parent()._init_widget.get(workerid, False)
        if value is None:
            if init:
                value = self._submodels[workerid][member]._get()
                if value is not None:
                    self._parent().gui_sets_value(workerid, member, value)
            else:
                self._variables_to_set.append((workerid, member))
        else:
            if init:
                self._submodels[workerid][member]._set(value)
            else:
                self._values_to_set.append((workerid, member, value))