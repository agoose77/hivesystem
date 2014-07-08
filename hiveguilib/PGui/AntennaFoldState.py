import weakref


class Antenna(object):

    def __init__(self, typ):
        self.typ = typ
        self.fold = False
        self.foldable = True

    def __str__(self):
        return ",".join((str(self.typ), str(self.fold)))


class AntennaFoldState(object):

    def __init__(self, nodecanvas, workermanager):
        self._sync = {}
        self._init_form = {}
        self._init_widget = {}
        self._nodecanvas = weakref.ref(nodecanvas)
        self._workermanager = weakref.ref(workermanager)
        self._pAntennaFoldState = self._AntennaFoldStateClass(self)
        self.states = {}

    def create_worker(self, workerid, antennas, guiparams):
        print("CREATE WORKER", antennas, workerid)
        state = {}
        for antenna_name, typ in antennas:
            antenna = Antenna(typ)

            if antenna_name in guiparams:
                antenna_params = guiparams[antenna_name]
                is_foldable = antenna_params.get("foldable", True)

                if not is_foldable:
                    antenna.foldable = False
                    fold = False

                else:
                    fold = antenna_params.get("fold", False)

                antenna.fold = fold
            state[antenna_name] = antenna

        if not state:
            state = None

        self.states[workerid] = state

    def remove_worker(self, workerid):
        state = self.states.pop(workerid)
        self._init_form.pop(workerid, None)
        self._init_widget.pop(workerid, None)
        self._sync.pop(workerid, None)
        if state is not None:
            self._pAntennaFoldState.remove_worker(workerid)

    def rename_worker(self, workerid, newid):
        state = self.states.pop(workerid)
        self.states[newid] = state
        for dictionary in self._init_form, self._init_widget, self._sync:
            if workerid not in dictionary:
                continue

            worker_data = dictionary.pop(workerid)
            dictionary[newid] = worker_data

        self._pAntennaFoldState.rename_worker(workerid, newid)

    def init_form(self, workerid, form):
        if workerid in self._init_form:
            return
        self._init_form[workerid] = True
        self._pAntennaFoldState.init_form(workerid, form)

    def init_widget(self, workerid, widget, controller):
        # If worker already initialised
        if workerid in self._init_widget:
            return

        self._init_widget[workerid] = True
        self._pAntennaFoldState.init_widget(workerid, widget, controller)

        state = self.states[workerid]
        if state is None:
            return

        for antenna_name in state:
            antenna = state[antenna_name]

            if antenna.fold:
                self._pAntennaFoldState.p_fold(workerid, antenna_name)

            else:
                self._pAntennaFoldState.p_expand(workerid, antenna_name)

    def gui_sets_value(self, workerid, member, value):
        variable = self._nodecanvas().get_antenna_connected_variable(workerid, member)
        self._workermanager()._update_variable(variable, value)


    def fold(self, workerid, member):
        antenna = self.states[workerid][member]
        assert not antenna.fold
        if not antenna.foldable:
            return
        antenna.fold = True

        folded, value = self._nodecanvas().fold_antenna_connection(workerid, member, antenna.typ, called_on_load=False)
        if not folded:
            antenna.fold = False
            return
        if workerid in self._init_widget:
            self._pAntennaFoldState.p_fold(workerid, member)
        self._pAntennaFoldState.p_set_value(workerid, member, value)

    def gui_folds(self, workerid, member):
        self.fold(workerid, member)

    def gui_expands(self, workerid, member):
        self.expand(workerid, member)

    def expand(self, workerid, member):
        antenna = self.states[workerid][member]
        if not antenna.fold:
            return
        antenna.fold = False
        self._nodecanvas().expand_antenna_connection(workerid, member)
        if workerid in self._init_widget:
            self._pAntennaFoldState.p_expand(workerid, member)

    def p(self):
        return self._pAntennaFoldState

    def sync(self, workerid, onload):
        """
        Synchronizes all folded variables
        If a folded antenna has a connection:
          Retrieve the variable and update the parameter GUI
        If not:
          Create a new variable based on the parameter GUI
        """
        state = self.states[workerid]
        if state is None:
            return

        if workerid in self._sync:
            return
        if workerid in self._init_widget:
            return

        assert workerid not in self._sync, workerid
        assert workerid not in self._init_widget, workerid
        self._sync[workerid] = True

        for antenna_name in state:
            antenna = state[antenna_name]
            if not onload and not antenna.fold:
                continue

            folded, value = self._nodecanvas().fold_antenna_connection(workerid, antenna_name, antenna.typ, onload)
            if not folded:
                antenna.fold = False
                continue

            antenna.fold = True
            self._pAntennaFoldState.p_set_value(workerid, antenna_name, value)
