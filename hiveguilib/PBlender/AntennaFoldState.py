import weakref
from functools import partial
from ..HBlender.BlenderWidgets import *


class AntennaFoldState(object):
    _idcount = 0

    def __init__(self, parent):
        self._parent = weakref.ref(parent)
        self._widgets = {}
        self._submodels = {}
        self._idmap = {}
        self._idmaprev = {}
        self._values_to_set = []
        self._variables_to_set = []

    def p_expand(self, workerid, a):
        if a not in self._widgets[workerid]: return
        for on, off in self._widgets[workerid][a]:
            on()

    def gui_expands(self, numid, a):
        workerid = self._idmaprev[numid]
        self._parent().gui_expands(workerid, a)

    def p_fold(self, workerid, a):
        if a not in self._widgets[workerid]: return
        for on, off in self._widgets[workerid][a]:
            off()

    def gui_folds(self, numid, a):
        workerid = self._idmaprev[numid]
        self._parent().gui_folds(workerid, a)

    def gui_sets_value(self, numid, a, value):
        workerid = self._idmaprev[numid]
        self._parent().gui_sets_value(workerid, a, value)

    def init_form(self, workerid, form):
        p = self._parent()
        state = p.states[workerid]
        if state is None: return
        for a in state:
            ele = getattr(form, a, None)
            if ele is None: continue
            name = getattr(ele, "name", a)
            ele.add_button("Expand %s" % name, "before")
            antenna = state[a]
            if antenna.foldable:
                ele.add_button("Fold %s" % name, "before")

    def init_widget(self, workerid, widget, controller):
        parent_pgui = self._parent()
        state = parent_pgui.states[workerid]

        if state is None:
            return

        view = controller._view()
        model = controller._model()
        self._widgets[workerid] = {}
        self._submodels[workerid] = {}

        id_count = self._idcount
        self._idcount += 1

        self._idmap[workerid] = id_count  # remains constant throughout lifetime
        self._idmaprev[id_count] = workerid

        for antenna_name in state:
            antenna = state[antenna_name]
            widgets = []
            element = getattr(view, antenna_name, None)
            if element is None:
                continue

            if not hasattr(element, "widget"):
                raise Exception("Unfoldable: %s.%s has no associated widget in parameter tab" % (workerid, antenna_name))

            widget = element.widget
            on, off = widget.show, widget.hide

            widgets.append((off, on))  # expand / fold

            if antenna.foldable:
                fold_button = element.buttons[1]  # Fold button
                fold_button.listen(partial(self.gui_folds, id_count, antenna_name))

                on, off = fold_button.show, fold_button.hide
                widgets.append((on, off))  # expand / fold

            fold_button = element.buttons[0]  # Expand button
            fold_button.listen(partial(self.gui_expands, id_count, antenna_name))

            on, off = fold_button.show, fold_button.hide
            widgets.append((off, on))  # expand / fold

            self._widgets[workerid][antenna_name] = widgets

            sub_model = getattr(model, antenna_name, None)
            self._submodels[workerid][antenna_name] = sub_model
            sub_model._listen(partial(self.gui_sets_value, id_count, antenna_name))

        current_values = [v for v in self._values_to_set if v[0] == workerid]
        self._values_to_set = [v for v in self._values_to_set if v[0] != workerid]
        handled = set()

        for worker_id, member, value in current_values:
            handled.add(member)
            self._submodels[workerid][member]._set(value)

        current_values = [v for v in self._variables_to_set if v[0] == workerid]
        self._variables_to_set = [v for v in self._variables_to_set if v[0] != workerid]
        for worker_id, member in current_values:
            if member in handled:
                continue

            value = self._submodels[workerid][member]._get()
            if value is not None:
                self._parent().gui_sets_value(workerid, member, value)

    def remove_worker(self, workerid):
        if not workerid in self._widgets:
            return

        self._widgets.pop(workerid)
        self._submodels.pop(workerid)
        numid = self._idmap.pop(workerid)
        self._idmaprev.pop(numid)

    def rename_worker(self, workerid, newid):
        if not workerid in self._widgets:
            return

        w = self._widgets.pop(workerid)
        self._widgets[newid] = w
        s = self._submodels.pop(workerid)
        self._submodels[newid] = s
        numid = self._idmap.pop(workerid)
        self._idmaprev[numid] = newid

    def p_set_value(self, workerid, member, value):
        assert self._parent().states[workerid][member].fold == True, (workerid, member)
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