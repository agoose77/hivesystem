from . import PGui
import weakref


class PSpyderhive(PGui):
    _PSpyderhiveClass = None

    def __init__(self, mainwindow, title):
        self._mainwindow = mainwindow
        self._subwin = mainwindow.newSubWindow(title)
        self._pSpyderhive = self._PSpyderhiveClass(self, self._subwin)
        self._spydermapmanager = None

    def set_spydermapmanager(self, spydermapmanager):
        self._spydermapmanager = weakref.ref(spydermapmanager)

    def set_spyderhive_candidates(self, candidates):
        self._pSpyderhive.set_candidates(candidates)

    def update_spyderhive(self, spyderhive):
        self._pSpyderhive.set_spyderhive(spyderhive)

    def _set_spyderhive(self, spyderhive):
        return self._spydermapmanager().gui_sets_spyderhive(spyderhive)

    def set_spyderhive(self, spyderhive):
        self.update_spyderhive(spyderhive)
        self._set_spyderhive(spyderhive)

    def gui_sets_spyderhive(self, spyderhive):
        return self._set_spyderhive(spyderhive)

    def p(self):
        return self._pSpyderhive
  
