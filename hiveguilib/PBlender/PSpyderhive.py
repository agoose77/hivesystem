import logging, bpy

class PSpyderhive(object):
  def __init__(self, parent, parentwidget):
    self._parent = parent
    self.mainWin = parentwidget.parent
    from ..HBlender.BlendManager import blendmanager    
    blendmanager.spyderhive_widget.listen(self.update)
  def set_candidates(self, candidates):
    from ..HBlender.BlendManager import blendmanager    
    blendmanager.spyderhive_widget.options = candidates
  def set_spyderhive(self, spyderhive):
    from ..HBlender.BlendManager import blendmanager    
    blendmanager.spyderhive_widget.set(spyderhive)    
  def update(self, spyderhive):
    space = bpy.context.space_data
    if space is None: return
    if space.tree_type == "Spydermap" and space.edit_tree is not None:
      if self.mainWin.nodetreemanager.name == space.edit_tree.name:
        self._parent.gui_sets_spyderhive(spyderhive)
  def __del__(self):
    blendmanager.spyderhive_widget.unlisten(self.update)
  
  
