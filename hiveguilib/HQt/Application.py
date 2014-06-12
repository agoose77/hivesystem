from __future__ import print_function, absolute_import

from . import HQt

from .anyQt import QtGui

class Application(HQt):
  def __init__(self, argv):
    self._qt = QtGui.QApplication(argv)
  def qt(self): 
    return self._qt  
  def mainloop(self): 
    return self._qt.exec_()
    
