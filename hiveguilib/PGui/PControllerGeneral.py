from . import PGui
import weakref


class PControllerGeneral(PGui):
    _PControllerGeneralClass = None

    def __init__(self):
        self._pControllerGeneral = self._PControllerGeneralClass(self)
        self._workermanager = None
        self._pwindow = None
        self._workerid = None

    def set_workermanager(self, workermanager):
        self._workermanager = weakref.ref(workermanager)

    def set_workerinstancemanager(self, workerinstancemanager):
        self._wim = weakref.ref(workerinstancemanager)

    def set_pwindow(self, pwindow):
        self._pwindow = weakref.ref(pwindow)

    def show(self):
        self._pControllerGeneral.show()

    def hide(self):
        self._pControllerGeneral.hide()
        self._workerid = None

    def load_paramset(self, workerid):
        manager = self._workermanager()
        p = manager.get_parameters(workerid)
        profile = None
        type_ = "worker"
        tooltip = ""
        try:
            instance = self._wim().get_workerinstance(workerid)
            profile = instance.curr_profile
            type_ = instance.type
            tooltip = instance.tooltip
        except KeyError:
            pass
        workertype, params, metaparams = p
        cont = self._pControllerGeneral
        cont.set_values(workerid, workertype, type_, profile, tooltip)
        self._workerid = workerid

    def refresh(self):
        if self._workerid is None: return
        self.load_paramset(self._workerid)

    def update_paramvalues(self, paramdict):
        if "workerid" in paramdict:
            new_workerid = paramdict["workerid"]
            self._controller_rename_worker(new_workerid)

    def set_paramvalues(self, paramdict):
        if "workerid" in paramdict:
            self._workermanager.rename_worker(new_workerid)
            self._controller_rename_worker(new_workerid)

    def _controller_rename_worker(self, new_workerid):
        cont = self._pControllerGeneral
        new_workerid = str(new_workerid)
        cont.update_parameter("workerid", new_workerid)
        self._workerid = new_workerid

    def gui_renames_worker(self, new_workerid):
        new_workerid = str(new_workerid)
        mgr = self._workermanager()
        ok = mgr.gui_renames_worker(self._workerid, new_workerid)
        if not ok: return False
        self._workerid = new_workerid
        return True

    def p(self):
        return self._pControllerGeneral
  
