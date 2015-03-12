from __future__ import print_function, absolute_import

import weakref


class PWindow(object):

    def __init__(self, mainwindow, subwindowname, controller):
        self.subwindowname = subwindowname
        self._mainwindow = mainwindow
        self._subwin = mainwindow.newSubWindow(subwindowname)
        self._controller = controller
        self._controller.set_pwindow(self)
        self._pmanager = None

    def setPManager(self, pmanager):
        self._pmanager = weakref.ref(pmanager)

    def pmanager(self):
        if self._pmanager is None: return None
        return self._pmanager()

    def hide(self):
        self._controller.hide()
        self._subwin.hide()

    def deselect(self):
        self.hide()

    def show(self):
        self._controller.show()
        self._subwin.show()

    def load_paramset(self, id_):
        self._controller.load_paramset(id_)
        self.show()

    def set_paramvalues(self, *args, **kwargs):
        """
        Instructs the controller to set the Parameter values,
         letting the controller update the global state
        """
        self._controller.set_paramvalues(*args, **kwargs)

    def update_paramvalues(self, *args, **kwargs):
        """
        Instructs the controller update the view of the parameters
         with the following values, without making changes to the global state
        """
        self._controller.update_paramvalues(*args, **kwargs)


class PStaticWindow(PWindow):

    def hide(self):
        return

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.show()