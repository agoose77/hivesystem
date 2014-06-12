from __future__ import print_function, absolute_import


class HGui(object):
    def h(self):
        raise AttributeError("Abstract method HGui.h() must be re-implemented")


from .Node import Node, Attribute, Hook, Connection


def init(hmodule):
    globals()["hmodule"] = hmodule

    class Application(HGui):
        def __init__(self, argv):
            self._hApplication = hmodule.Application(argv)

        def h(self):
            return self._hApplication

    globals()["Application"] = Application

    class MainWindow(HGui):
        def __init__(self):
            self._hMainWindow = hmodule.MainWindow()

        def setNodeCanvas(self, nodecanvas):
            self._hMainWindow.setNodeCanvas(nodecanvas.h())

        def newSubWindow(self, name):
            return self._hMainWindow.newSubWindow(name)

        def getSubWindow(self, name):
            return self._hMainWindow.getSubWindow(name)

        def show(self):
            return self._hMainWindow.show()

        def popup(self, title, options):
            return self._hMainWindow.popup(title, options)

        def supports_popup(self):
            return self._hMainWindow.supports_popup()

        def h(self):
            return self._hMainWindow

    globals()["MainWindow"] = MainWindow

    from .NodeCanvas import NodeCanvas as N

    class NodeCanvas(N):
        _NodeCanvasClass = hmodule.NodeCanvas

    globals()["NodeCanvas"] = NodeCanvas

    globals()["FileDialog"] = hmodule.FileDialog
    globals()["StatusBar"] = hmodule.StatusBar
