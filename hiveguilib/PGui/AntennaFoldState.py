import weakref


class Antenna(object):

    def __init__(self, typ):
        self.typ = typ
        self.initial_fold = False
        self.is_folded = False
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

                antenna.initial_fold = fold

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

        # COPY SECTION
        state = self.states[workerid]
        if state is None:
            return

        for antenna_name in state:
            antenna = state[antenna_name]

            if not antenna.foldable:
                continue

            # Set the antenna.fold value from the GUI ( if at 0,0 its folded else not)
            should_be_folded = self._nodecanvas().check_default_folded(workerid, antenna_name)

            if should_be_folded is None:
                should_be_folded = antenna.initial_fold

            if not antenna.is_folded and should_be_folded:
                self.fold(workerid, antenna_name)

        #END COPY SECTION

        self._init_widget[workerid] = True
        self._pAntennaFoldState.init_widget(workerid, widget, controller)

        state = self.states[workerid]
        if state is None:
            return

        for antenna_name in state:
            antenna = state[antenna_name]

            if antenna.is_folded:
                self._pAntennaFoldState.p_fold(workerid, antenna_name)

            else:
                self._pAntennaFoldState.p_expand(workerid, antenna_name)

    def gui_sets_value(self, worker_id, member, value):
        variable = self._nodecanvas().get_folded_variable(worker_id, member)
        self._workermanager()._update_variable(variable, value)

    def fold(self, worker_id, member):
        antenna = self.states[worker_id][member]
        assert not antenna.is_folded
        if not antenna.foldable:
            return

        try:
            # Be careful, any select() operation will have this called again if we're initialising
            value = self._nodecanvas().fold_antenna_connection(worker_id, member, antenna.typ)

        except RuntimeWarning:
            return

        antenna.is_folded = True

        if worker_id in self._init_widget:
            self._pAntennaFoldState.p_fold(worker_id, member)

        self._pAntennaFoldState.p_set_value(worker_id, member, value)

    def gui_folds(self, workerid, member):
        print("GUI FOLD")
        self.fold(workerid, member)

    def gui_expands(self, workerid, member):
        self.expand(workerid, member)

    def expand(self, workerid, member):
        antenna = self.states[workerid][member]
        if not antenna.is_folded:
            return

        antenna.is_folded = False
        self._nodecanvas().expand_antenna_connection(workerid, member)

        if workerid in self._init_widget:
            self._pAntennaFoldState.p_expand(workerid, member)

    def p(self):
        return self._pAntennaFoldState