from . import PGui
import weakref


class PControllerBlock(PGui):
    _PControllerBlockClass = None

    def __init__(self):
        self._pControllerBlock = self._PControllerBlockClass(self)
        self._workermanager = None
        self._pwindow = None
        self._workerid = None
        self._block = None

    def set_workermanager(self, workermanager):
        self._workermanager = weakref.ref(workermanager)

    def set_workerinstancemanager(self, workerinstancemanager):
        self._wim = weakref.ref(workerinstancemanager)

    def set_pwindow(self, pwindow):
        self._pwindow = weakref.ref(pwindow)

    def show(self):
        self._pControllerBlock.show()

    def hide(self):
        self._pControllerBlock.hide()
        self._workerid = None

    def load_paramset(self, workerid):
        manager = self._workermanager()
        block = manager.get_block(workerid)
        self._block = block
        blockvalues = None
        try:
            instance = self._wim().get_workerinstance(workerid)
            blockvalues = instance.curr_blockvalues
        except KeyError:
            pass
        self._workerid = workerid
        cont = self._pControllerBlock
        if self._block is None:
            cont.set_blocktype(None)
            cont.set_blockstrings(None)
            cont.set_blockvalues(None)
        else:
            cont.set_blocktype(self._block.spydertype)
            cont.set_blockstrings(self._block.tree.keys())
            cont.set_blockvalues(blockvalues)

    def update_paramvalues(self, blockvalues):
        cont = self._pControllerBlock
        cont.set_blockvalues(blockvalues)

    def set_paramvalues(self, blockvalues):
        ok = self._update_blockvalues(blockvalues)
        assert ok is True
        self.update_paramvalues(blockvalues)
        self._wim().worker_update_blockvalues(self._workerid, blockvalues)

    def gui_updates_blockvalues(self, blockvalues):
        ok = self._update_blockvalues(blockvalues)
        if ok:
            self._wim().worker_update_blockvalues(self._workerid, blockvalues)
        return ok

    def _update_blockvalues(self, blockvalues):
        if self._block is None:
            assert blockvalues is None or blockvalues == [""] * len(blockvalues)
            return
        blockstrings = self._block.tree.keys()
        workerid = self._workerid
        io = self._block.io

        # Check that the name of the new blockvalues are valid
        for s in blockvalues:
            if s != "" and s not in blockvalues: return False

        #Make sure that you can't remove block antennas/outputs with connections
        instance = self._wim().get_workerinstance(workerid)
        old_blockvalues = instance.curr_blockvalues
        if old_blockvalues is not None:
            newvalues = list(blockvalues)
            for n in range(len(newvalues), len(old_blockvalues)):
                newvalues.append(None)
            has_connection = self._wim().has_connection
            for old, new in zip(old_blockvalues, newvalues):
                if not old: continue
                if not new or new != old:
                    if has_connection(workerid, io, old):
                        self.update_paramvalues(old_blockvalues)
                        return False

        return True


    def p(self):
        return self._pControllerBlock
  
