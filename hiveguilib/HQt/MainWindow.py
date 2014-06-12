from __future__ import print_function, absolute_import

from . import HQt
import weakref

from .anyQt import QtGui, QtCore
from .Layout import Layout

positions = {
 "left": QtCore.Qt.LeftDockWidgetArea,
 "right": QtCore.Qt.RightDockWidgetArea, 
 "top": QtCore.Qt.TopDockWidgetArea,
 "bottom": QtCore.Qt.BottomDockWidgetArea,
}

class widgetwrapper(object):
  def __init__(self, mainwin, wrapwidget, container):
    self._wrapwidget = wrapwidget
    self._mainwin = mainwin
    self._container = container
    xp = QtGui.QSizePolicy.Expanding
    self._wrapwidget.setSizePolicy(xp, xp)      
  def setWidget(self, widget):
    if isinstance(self._wrapwidget, QtGui.QDockWidget):
      self._wrapwidget.setWidget(widget)
    elif isinstance(self._wrapwidget, QtGui.QScrollArea):
      self._wrapwidget.setWidget(widget)
    elif isinstance(self._wrapwidget, QtGui.QStackedWidget):
      widgets = [self._wrapwidget.widget(n) for n in range(self._wrapwidget.count())]
      for w in widgets: self._wrapwidget.removeWidget(w)
      self._wrapwidget.insertWidget(0, widget)
      self._wrapwidget.setCurrentWidget(widget)
      xp = QtGui.QSizePolicy.Expanding
      widget.setSizePolicy(xp, xp)      
    else:
      raise TypeError(self._container)
    widget.updateGeometry()  
    self._wrapwidget.updateGeometry()  
  def wrapwidget(self):
    return self._wrapwidget
  def container(self):
    if self._container is None: return self._wrapwidget
    return self._container
  def hide(self):
    self.container().setVisible(False)
  def show(self):
    #KLUDGE: under Kubuntu 12.04 + PySide, tabs are drawn on top of each other for some reason 
    if self._wrapwidget.parent() is not None and "proptabs" in self._mainwin._subwindows \
     and self._wrapwidget.parent().parent() == self._mainwin._subwindows["proptabs"]._wrapwidget:
      t = self._mainwin._subwindows["proptabs"]._wrapwidget
      p = t.currentIndex()
      for i in range(t.count()): 
        if i != p:
          t.widget(i).setVisible(False)
        else:
          t.widget(i).setVisible(True)
      return
    
    self.container().setVisible(True)
  
class MainWindow(HQt, Layout):
  def __init__(self):  
    self._qt = QtGui.QMainWindow()
    self._subwindows = {}
    self._menus = {}
    self._menu_actions = []
    self._statusbar = QtGui.QStatusBar(self._qt)
    self._qt.setStatusBar(self._statusbar)
    self._parent_subwindows = set()
    
  def qt(self): 
    return self._qt  
  def show(self): 
    return self._qt.show()
  @staticmethod
  def emptyWidget():
    return QtGui.QWidget()
  def setNodeCanvas(self, nodecanvas):
    return self._qt.setCentralWidget(nodecanvas.qt())  
  def _newSubWindow(self, title, position):  
    pos = positions[position]
    win = QtGui.QDockWidget(title, self._qt)
    child = QtGui.QWidget()
    #child.setMinimumSize(200,200)
    win.setWidget(child)
    self._qt.addDockWidget(pos, win)
    return win
  def _newSubWidget(self, name, title, widget, parent):  
    p = self._subwindows[parent].wrapwidget()
    if widget == "tab":
      win = QtGui.QTabWidget()      
    elif widget == "form":
      win = QtGui.QScrollArea()
      layout = QtGui.QVBoxLayout()
      win.setLayout(layout)
    elif widget is None:
      win = QtGui.QStackedWidget()      
    else:
      raise ValueError(widget)
    xp = QtGui.QSizePolicy.Expanding
    win.setSizePolicy(xp, xp)
    
    ptab = isinstance(p, QtGui.QTabWidget)
    pdock = isinstance(p,QtGui.QDockWidget)
    pscroll = isinstance(p, QtGui.QScrollArea)
    if ptab:
      p.addTab(win, title)
      outerwin = None
    elif pdock or pscroll:
      if title is not None:
        outerwin = QtGui.QScrollArea()      
        outerwin.setSizePolicy(xp, xp)
        layout = QtGui.QVBoxLayout()
        outerwin.setLayout(layout)       
        label = QtGui.QLabel(title)
        layout.addWidget(label)
        layout.addWidget(win)
        win2 = outerwin
      else:
        outerwin = None
        win2 = win
      if pdock:
        assert parent not in self._parent_subwindows, parent
        self._parent_subwindows.add(parent)
        p.setWidget(win2)
      elif pscroll:
        l = p.layout()
        l.addWidget(win2)              
        
    else:
      raise TypeError((p, parent))
    
    #win.setMinimumSize(200,200)
    #win.show() #do we need this?
    return win, outerwin
  
  def newSubWindow(self, name, triggered = False):  
    if triggered:
      if name in self._subwindows: return self._subwindows[name]
    else:
      assert name not in self._subwindows, name
    win, outerwin, vis = self._layout(name)
    ret = widgetwrapper(self, win, outerwin)  
    if not vis: ret.hide()
    self._subwindows[name] = ret
    return ret    
          
  def getSubWindow(self, name):
    return self._subwindows[name]
  def getStatusBar(self):
    return self._statusbar  

  def add_menu(self, menuname):  
    assert menuname not in self._menus
    menu = self._qt.menuBar().addMenu(menuname)
    self._menus[menuname] = menu

  def add_menu_action(self, menuname, name, callback,
     icon = QtGui.QIcon(None), shortcut = None, statustip = None
   ):    
    action = QtGui.QAction(icon, name, self._qt)
    if shortcut is not None: action.setShortcut(shortcut)
    if statustip is not None: action.setStatusTip(statustip)
    action.triggered.connect(callback)
    self._menu_actions.append((menuname, name, callback, action))

    self._menus[menuname].addAction(action)
  
  def popup(self, title, options):
    menu = QtGui.QMenu(title)
    for option in options:
      menu.addAction(option)
    result = menu.exec_(QtGui.QCursor.pos())
    if not result: return None
    return result.text()
  def supports_popup(self): return True
  def close(self): self._qt.close()  
  
    
