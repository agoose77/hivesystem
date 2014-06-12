from __future__ import print_function, absolute_import


class HQt(object):
    def qt(self):
        raise AttributeError("Abstract method HQt.qt() must be re-implemented")


from ..HUtil.Attribute import Attribute, Hook
from .Application import Application
from .MainWindow import MainWindow
from .NodeCanvas import NodeCanvas
from .StatusBar import StatusBar


def FileDialog(mode):
    assert mode in ("save", "open", "dir"), mode
    from . import anyQt
    from .anyQt.QtGui import QFileDialog

    func = {
        "save": QFileDialog.getSaveFileName,
        "open": QFileDialog.getOpenFileName,
        "dir": QFileDialog.getExistingDirectory,
    }
    if anyQt._qt == "PyQt4":
        ret = func[mode]()
    else:  # PySide
        ret = func[mode]()[0]
    return ret
