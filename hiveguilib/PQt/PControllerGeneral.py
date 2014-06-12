import weakref
from .anyQt import QtGui, QtCore
from ..PGui.profiletypes import profiletypes, profiles_worker

class PControllerGeneral(object):
  label = "Worker"
  def __init__(self, parent):
    self._parent = weakref.ref(parent)
    self.widget = QtGui.QWidget()
    self.widget.setMinimumWidth(400) #kludge :(
    xp = QtGui.QSizePolicy.Expanding
    policy = QtGui.QSizePolicy(xp, xp)
    self.widget.setSizePolicy(policy)
    #self.widget.setWidgetResizable(True)          
    layout = QtGui.QFormLayout()
    self.l_workerid = QtGui.QLabel("%s ID" % self.label)
    self.w_workerid = QtGui.QLineEdit()
    layout.addRow(self.l_workerid, self.w_workerid)
    self.w_update = QtGui.QPushButton("Update ID")
    self.w_update.pressed.connect(self._update_id)
    layout.addWidget(self.w_update)
    self.w_cancel = QtGui.QPushButton("Cancel")
    self.w_cancel.pressed.connect(self._cancel_update_id)
    layout.addWidget(self.w_cancel)
    self.w_workertype = QtGui.QLineEdit()
    self.w_workertype.setReadOnly(True)
    layout.addRow("%s Type" % self.label, self.w_workertype)
    self.profiles = profiles_worker
    self.w_profile = QtGui.QComboBox()
    self.w_profile.addItems([v[1] for v in self.profiles])
    self.w_profile.activated.connect(self._update_profile)
    layout.addRow("%s Profile" % self.label, self.w_profile)

    self.widget.setLayout(layout)    
    policy = QtGui.QFormLayout.AllNonFixedFieldsGrow
    layout.setFieldGrowthPolicy(policy)
    self._added = False
    self.has_profile = False
    self._profile_index = -1
  def switch_profiles(self, newprofiles):
    if newprofiles == self.profiles: return
    for i in self.profiles: 
      self.w_profile.removeItem(0)
    self.profiles = newprofiles  
    self.w_profile.addItems([v[1] for v in self.profiles])    
  def set_values(self, workerid, workertype, profiletype, profile):
    newprofiles = profiletypes[profiletype]
    self.switch_profiles(newprofiles)
    self.w_workerid.setText(workerid)
    self.w_workertype.setText(workertype)
    self.l_workerid.setText("%s ID" % self.label)    
    self._workerid = workerid
    self.has_profile = False
    if profile is not None:
      for i,pr in enumerate(self.profiles):
        if pr[0] == profile:
          self._profile_index = i
          self.has_profile = True
          break
    if not self.has_profile:
      self._profile_index = -1
    self.w_profile.setCurrentIndex(self._profile_index)
      
  def _update_profile(self, index):
    profile = self.profiles[index][0]
    if self.has_profile:
      parent = self._parent()
      try:
        parent._wim().morph_worker(self._workerid, profile)
        self._profile_index = index
      except KeyError:
        self.w_profile.setCurrentIndex(self._profile_index)
      self.w_profile.setCurrentIndex(self._profile_index)  
  def _update_id(self):
    new_workerid = self.w_workerid.text()
        
    if new_workerid == self._workerid: return
    parent = self._parent()
    pwindow = parent._pwindow()
    pmanager = pwindow.pmanager()
    ok1 = parent.gui_renames_worker(new_workerid)
    if not ok1: 
      self.l_workerid.setText("<font color=red>%s ID</font>" % self.label)
      return
    if pmanager is not None:
      ok2 = pmanager.gui_renames_pwidget(self._workerid, new_workerid)
      assert ok2 == True
    self.l_workerid.setText("%s ID" % self.label)
    self._workerid = new_workerid  
  def _cancel_update_id(self):
    self.l_workerid.setText("%s ID" % self.label)
    self.w_workerid.setText(self._workerid)
  def show(self):
    if not self._added:
      parent = self._parent()
      pwindow = parent._pwindow()
      subwin = pwindow._subwin
      subwin.setWidget(self.widget)
      self._added = True
    self.widget.show()  

  def hide(self):
    self.widget.hide()
