from . import HQt


class StatusBar(HQt):
    def __init__(self, mainwindow):
        self._statusbar = mainwindow.h()._statusbar

    def setMessage(self, message):
        self._statusbar.showMessage(message)

    def clearMessage(self):
        self._statusbar.clearMessage()

    def qt(self):
        return self._statusbar
