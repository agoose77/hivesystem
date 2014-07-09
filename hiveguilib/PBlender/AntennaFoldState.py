import weakref
from functools import partial
from ..HBlender.BlenderWidgets import *
from .. import PersistentIDManager

class AntennaFoldState(object):

    def __init__(self, parent):
        self._parent = weakref.ref(parent)
        self._widgets = {}
        self._submodels = {}
        self._idmap = {}
        self._idmaprev = {}
        self._values_to_set = []
        self._variables_to_set = []
        self._persistent_id_manager = PersistentIDManager()

    def p_expand(self, workerid, antenna_name):
        if antenna_name not in self._widgets[workerid]:
            return

        for show, hide in self._widgets[workerid][antenna_name]:
            show()

    def gui_expands(self, persistent_id, antenna_name):
        worker_id = self._persistent_id_manager.get_temporary_id(persistent_id)
        self._parent().gui_expands(worker_id, antenna_name)

    def p_fold(self, workerid, antenna_name):
        if antenna_name not in self._widgets[workerid]:
            print("But couldn't find widget")
            return

        for show, hide in self._widgets[workerid][antenna_name]:
            hide()

    def gui_folds(self, persistent_id, antenna_name):
        worker_id = self._persistent_id_manager.get_temporary_id(persistent_id)
        self._parent().gui_folds(worker_id, antenna_name)

    def gui_sets_value(self, persistent_id, antenna_name, value):
        worker_id = self._persistent_id_manager.get_temporary_id(persistent_id)
        print("SET VALUAES")
        self._parent().gui_sets_value(worker_id, antenna_name, value)

    def init_form(self, worker_id, form):
        parent = self._parent()
        state = parent.states[worker_id]

        if state is None:
            return

        for antenna_name in state:
            element = getattr(form, antenna_name, None)
            if element is None:
                continue

            name = getattr(element, "name", antenna_name)
            element.add_button("Expand %s" % name, "before")
            antenna = state[antenna_name]

            if antenna.foldable:
                element.add_button("Fold %s" % name, "before")

    def init_widget(self, worker_id, widget, controller):
        parent_pgui = self._parent()
        state = parent_pgui.states[worker_id]

        if state is None:
            return

        view = controller._view()
        model = controller._model()

        self._widgets[worker_id] = {}
        self._submodels[worker_id] = {}

        persistent_id = self._persistent_id_manager.create_persistent_id(worker_id)

        for antenna_name in state:
            antenna = state[antenna_name]
            widgets = []
            element = getattr(view, antenna_name, None)
            if element is None:
                continue

            if not hasattr(element, "widget"):
                raise Exception("Unfoldable: %s.%s has no associated widget in parameter tab" % (worker_id, antenna_name))

            widget = element.widget
            show, hide = widget.show, widget.hide

            widgets.append((hide, show))  # expand / fold

            if antenna.foldable:
                fold_button = element.buttons[1]  # Fold button
                fold_button.listen(partial(self.gui_folds, persistent_id, antenna_name))

                show, hide = fold_button.show, fold_button.hide
                widgets.append((show, hide))  # expand / fold

            fold_button = element.buttons[0]  # Expand button
            fold_button.listen(partial(self.gui_expands, persistent_id, antenna_name))

            show, hide = fold_button.show, fold_button.hide
            widgets.append((hide, show))  # expand / fold

            self._widgets[worker_id][antenna_name] = widgets

            sub_model = getattr(model, antenna_name, None)
            self._submodels[worker_id][antenna_name] = sub_model
            sub_model._listen(partial(self.gui_sets_value, persistent_id, antenna_name))

        current_values = [v for v in self._values_to_set if v[0] == worker_id]
        self._values_to_set = [v for v in self._values_to_set if v[0] != worker_id]
        handled = set()

        for worker_id, member, value in current_values:
            handled.add(member)
            self._submodels[worker_id][member]._set(value)

        current_values = [v for v in self._variables_to_set if v[0] == worker_id]
        self._variables_to_set = [v for v in self._variables_to_set if v[0] != worker_id]
        for worker_id, member in current_values:
            if member in handled:
                continue

            value = self._submodels[worker_id][member]._get()
            if value is not None:
                self._parent().gui_sets_value(worker_id, member, value)

    def remove_worker(self, worker_id):
        if not worker_id in self._widgets:
            return

        self._widgets.pop(worker_id)
        self._submodels.pop(worker_id)
        self._persistent_id_manager.remove_with_temporary_id(worker_id)

    def rename_worker(self, old_id, new_id):
        if not old_id in self._widgets:
            return

        widget = self._widgets.pop(old_id)
        self._widgets[new_id] = widget
        submodel = self._submodels.pop(old_id)
        self._submodels[new_id] = submodel

        self._persistent_id_manager.change_temporary_with_temporary_id(old_id, new_id)

    def p_set_value(self, worker_id, member, value):
        assert self._parent().states[worker_id][member].is_folded == True, (worker_id, member)
        init = self._parent()._init_widget.get(worker_id, False)

        if value is None:
            if init:
                value = self._submodels[worker_id][member]._get()
                if value is not None:
                    self._parent().gui_sets_value(worker_id, member, value)
            else:
                self._variables_to_set.append((worker_id, member))
        else:
            if init:
                m = self._submodels[worker_id][member]
                for l in m._listeners:
                    if not hasattr(l, "args"):
                        continue

                self._submodels[worker_id][member]._set(value)
            else:
                self._values_to_set.append((worker_id, member, value))