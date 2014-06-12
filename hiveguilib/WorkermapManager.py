from __future__ import print_function, absolute_import

import os
import spyder, Spyder

from .workergen import workergen

class WorkermapManager(object):
  def __init__(self, mainwin, workermanager, workerinstancemanager, file_dialog):
    self._mainwin = mainwin
    self._wim = workerinstancemanager
    self._workermanager = workermanager
    self._file_dialog = file_dialog

    self._lastsave = None
    self._dialogs = [] #TODO: get rid of closed dialogs..
    
    win = self._mainwin.h()
    win.add_menu("&File")
    win.add_menu_action(
     "&File",
     "&New",
     self.clear,
     shortcut = "Ctrl+N",
     statustip = "Close the current Workermap file and open a new one",
    )
    win.add_menu_action(
     "&File",
     "&Open",
     self.menu_load,
     shortcut = "Ctrl+O",
     statustip = "Open a Workermap file",
    )
    win.add_menu_action(
     "&File",
     "&Save",
     self.menu_save,
     shortcut = "Ctrl+S",
     statustip = "Save the current Workermap file",
    )
    win.add_menu_action(
     "&File",
     "Save as",
     self.menu_save_as,
     statustip = "Save the current Workermap file in the desired location",
    )
    win.add_menu_action(
     "&File",
     "&Quit",
     win.close,
     shortcut = "Ctrl+Q",
     statustip = "Quits the editor",
    )
    win.add_menu("&Generate")
    win.add_menu_action(
     "&Generate",
     "&Generate code",
     self.generate,
     shortcut = "Ctrl+G",
     statustip = "Generate Python code",
    )

  def _load(self, workermap):
    for seg in workermap.segments:
      x, y = seg.position.x, seg.position.y
      metaparamvalues = None
      if seg.metaparameters is not None:
        metaparamvalues = {}
        for param in seg.metaparameters:
          metaparamvalues[param.pname] = param.pvalue
      paramvalues = None
      if seg.parameters is not None:
        paramvalues = {}
        for param in seg.parameters:
          paramvalues[param.pname] = param.pvalue
      try:
        self._workermanager.instantiate(
         seg.segid, seg.segtype, x, y, metaparamvalues, paramvalues
        )
        if seg.profile != "default":
          self._wim.morph_worker(seg.segid, seg.profile)
      except KeyError:
        print("Unknown segment:", seg.segtype, seg.segid.split(".")[-1])
        continue  
    
    count = 0
    for con in workermap.connections:
      count += 1
      con_id = "con-%d" % count
      interpoints = [(ip.x, ip.y) for ip in con.interpoints]
      self._wim.add_connection(
        con_id,
        (con.start.segid, con.start.io),
        (con.end.segid, con.end.io),
        interpoints,    
      )
  
  def load(self, workermapfile):
    self.clear()  
    
    #Just to find Spyder models...
    workermanager = self._workermanager
    localdir = os.path.split(workermapfile)[0]
    workermanager.find_local_workers(localdir)
    self._workerfinder_local = None
    
    workermap = Spyder.Workermap.fromfile(workermapfile)
    self._load(workermap)

  def _build_workermap(self):
    workermanager = self._workermanager
    segments, connections = [], []
    for segid in sorted(workermanager.workerids()):
      node, mapping = self._wim.get_node(segid)
      if node.empty: continue
      segtype, params, metaparams = workermanager.get_parameters(segid)
      if params is not None: params = params.items()
      if metaparams is not None: metaparams = metaparams.items()
      profile = self._wim.get_workerinstance(segid).curr_profile
      
      seg = Spyder.WorkerSegment (
        segid,
        segtype,
        node.position,
        parameters = params,
        metaparameters = metaparams,
        profile = profile,
      )
      segments.append(seg)
    for c in self._wim.get_connections():  
      start_node, start_mapping = self._wim.get_node(c.start_node)
      if start_mapping is None: raise KeyError(c.start_node)
      end_node, end_mapping = self._wim.get_node(c.end_node)
      if end_mapping is None: raise KeyError(c.end_node)      
      start_attribute = start_mapping._outmapr[c.start_attribute]
      end_attribute = end_mapping._inmapr[c.end_attribute]
      con = Spyder.WorkerSegmentConnection (
        (c.start_node, start_attribute),
        (c.end_node, end_attribute),
        c.interpoints
      )
      connections.append(con)
    workermap = Spyder.Workermap(segments, connections)
    return workermap

  def save(self, workermapfile, filesaver = None):
    workermap = self._build_workermap()
    if filesaver:
      filesaver(workermapfile, str(workermap))
    else:
      workermap.tofile(workermapfile)
    self._lastsave = workermapfile
    return workermap

  def menu_save_as(self):
    workermapfile = self._file_dialog("save")
    self.save(workermapfile)  

  def menu_save(self):
    if self._lastsave is None:
      return self.menu_save_as()
    self.save(self._lastsave)  

  def menu_load(self):
    workermapfile = self._file_dialog("open")
    self.load(workermapfile)  
    self._lastsave = workermapfile

  def clear(self):
    self._workermanager.clear_workers()
    
  def generate(self):
    workermap = self._build_workermap()
    name = "myworker"
    if self._lastsave is not None:
      f = os.path.split(self._lastsave)[1]
      name = f.split(".")[-2:][0]
    code = None  
    try:
      code = workergen(name, workermap)
      from .HQt.anyQt import QtGui
      from .PQt.pythoncode import highlight, set_css                
      dialog = QtGui.QDialog()
      dialog.setMinimumSize(600,800)
      dialog.setModal(False)
      dialog.setWindowTitle("Generated Python code for '%s'" % name)
      textedit = QtGui.QTextEdit(parent=dialog)
      textedit.setMinimumSize(600,800)
      dialog.show()
      textedit.append(code)
      self._dialogs.append(dialog)
      set_css(textedit)
      highlight(textedit)
    except:      
      import traceback
      traceback.print_exc()
      if code is not None: print(code)
    
