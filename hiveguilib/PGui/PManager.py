from __future__ import print_function, absolute_import

from . import PGenerator
class PManager(object):
  def  __init__(self, pwins):
    self._pwins = pwins
    self._pwidgets = {} #TODO: make sure this does not take too much memory! maximize to last 10-100 elements?
    self._parwidgetname = None
    for pwin in pwins.values():
      pwin.setPManager(self)
    self.modifiers = []
  def deselect(self):
    for pwin in self._pwins.values():
      pwin.deselect()  
    self._parwidgetname = None
  def get_pwindow(self, pwindow):
    return self._pwins[pwindow]
  def select_pwidget(self, id_, pwindow,
   paramnames, paramtypelist, paramvalues, 
   update_callback, buttons = [], form_manipulators = []
  ):
    if len(paramnames) == 0:
      self._pwins[pwindow].deselect()
      return None, None
    if id_ not in self._pwidgets:
      self._pwidgets[id_] = {}
    pwidgets = self._pwidgets[id_]
    if pwindow not in pwidgets:
      parwidget, controller = PGenerator(
       paramnames, paramtypelist, paramvalues, 
       update_callback, 
       buttons, form_manipulators
      )
      pwidgets[pwindow] = parwidget, controller
      for m in self.modifiers:
        m("new", parwidget, controller)
    else:   
      parwidget, controller = pwidgets[pwindow]
    self._pwins[pwindow].setWidget(parwidget)  
    self._parwidgetname = id_
    return parwidget, controller
  def gui_renames_pwidget(self, old_id, new_id):
    self._rename_pwidget(old_id, new_id)
    return True
  def _rename_pwidget(self, old_id, new_id):
    if old_id == new_id: return
    if old_id not in self._pwidgets: return
    assert new_id not in self._pwidgets, new_id
    pwidgets = self._pwidgets.pop(old_id) 
    self._pwidgets[new_id] = pwidgets
  def rename_pwidget(self, old_id, new_id):
    self._rename_pwidget(old_id, new_id)
    if "general" in self._pwins:
      pwin_general = self._pwins["general"]
      if pwin_general._controller._workerid == old_id:
        pwin_general.load_paramset(new_id) 
  def delete_pwidget(self, id_):
    if id_ not in self._pwidgets: return
    pwidgets = self._pwidgets.pop(id_)
    for parwidget, controller in pwidgets.values():
      for m in self.modifiers:
        m("delete", parwidget, controller)    
    if self._parwidgetname == id_: 
      self.deselect()
