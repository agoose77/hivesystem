import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *

from .bglnode import bglnode

import functools

has_bgl = False
try:
  from bgl import *
  has_bgl = True
except ImportError:
  pass

def build_canvasdrone(wrappedclass, classname, drawshow, drawshowtype,  baseclass):
  baseklass = baseclass
  assert drawshow in ("draw", "show"), drawshow
  if hasattr(baseclass, "_wrapped_hive") and callable(baseclass._wrapped_hive):
    baseklass = baseclass._wrapped_hive
  class buildclass(baseclass):
    def __init__(self):
      self._nodes = {}
      self._boxes = {}
      self.drawshowinstances = {}
      self._canvasobjects = {}
      self._classname = self.__class__.__name__.rstrip("&")
      
      baseklass.__init__(self)  
      self._render2d = None
      self._aspect2d = None
      self._pixel2d = None
      self._sortids = set()
      self._next_sortid = 1
    def _get_next_sortid(self):
      ret = self._next_sortid
      self._sortids.add(ret)
      self._next_sortid += 1
      return ret
    def _set_render2d(self,get_render2d):
      self.get_render2d = get_render2d
    def _set_aspect2d(self,get_aspect2d):
      self.get_aspect2d = get_aspect2d
    def _set_pixel2d(self,get_pixel2d):
      self.get_pixel2d = get_pixel2d

    def get_2d(self, box):  
      if box.mode == "pixels":
        twod = self.get_pixel2d()
      elif box.mode == "standard":
        twod = self.get_render2d()
      elif box.mode == "aspect":
        twod = self.get_aspect2d()
      else:
        raise ValueError(box.mode)  
      return twod

    def _get_parent_bglnode(self, identifier, box):
      twod = self.get_2d(box)
      node = bglnode(identifier+"-pivot")
      node.setPos(box.x,box.y+box.sizey,0)
      node.setScale(box.sizex,box.sizey,1)
      node.reparentTo(twod)
      return node
    
    def _draw(self, obj, identifier, box, parameters=None):    
      self._nodes[identifier] = self._get_parent_bglnode(identifier, box)
      self.drawshowinstances[identifier] = wrappedclass(self, obj, identifier, parameters)
      self._nodes[identifier].children = [self.drawshowinstances[identifier]]
      self._boxes[identifier] = box
    def _show(self, obj, identifier, parameters=None):    
      self.drawshowinstances[identifier] = wrappedclass(self, obj, identifier, parameters)
    def _update_draw(self, obj, identifier, box, parameters=None):    
      if box is not self._boxes[identifier]:
        newnode = self._get_parent_bglnode(identifier, box)
        ret = self.drawshowinstances[identifier].update(obj, identifier, parameters)
        if ret is not None: self.drawshowinstances[identifier] = ret
        self._nodes[identifier].removeNode()
        self._nodes[identifier] = newnode
        self._nodes[identifier].children = [self.drawshowinstances[identifier]]
        self._boxes[identifier] = box
      else:
        ret = self.drawshowinstances[identifier].update(obj, identifier, parameters)
        if ret is not None: self.drawshowinstances[identifier] = ret        
    def _update_show(self, obj, identifier, parameters=None):    
      ret = self.drawshowinstances[identifier].update(obj, identifier, parameters)
      if ret is not None: self.drawshowinstances[identifier] = ret
    def _remove0(self, identifier):
      self.drawshowinstances[identifier].remove()
      self.drawshowinstances.pop(identifier)
      if identifier in self._nodes:
        self._nodes[identifier].removeNode()
        self._nodes.pop(identifier)

    def get_canvas_size(self, canvas_sizefunc):
      self.canvas_size = canvas_sizefunc
              
    def place(self):
      if not has_bgl: raise ImportError("Cannot import bgl")

      libcontext.socket(("blender", "noderoot", "pixel2d"), socket_single_required(self._set_pixel2d))
      libcontext.socket(("blender", "noderoot", "render2d"), socket_single_required(self._set_render2d))
      libcontext.socket(("blender", "noderoot", "aspect2d"), socket_single_required(self._set_aspect2d))
      libcontext.socket(("canvas","size"), socket_single_required(self.get_canvas_size))
      
      if drawshow == "draw":
        libcontext.plugin(("canvas", "draw", drawshowtype), plugin_supplier(self._draw))
        libcontext.plugin(("canvas", "update", drawshowtype), plugin_supplier(self._update_draw))
      else:
        libcontext.plugin(("canvas", "show", drawshowtype), plugin_supplier(self._show))
        libcontext.plugin(("canvas", "update", drawshowtype), plugin_supplier(self._update_show))
      libcontext.plugin(("canvas", "remove", drawshowtype), plugin_supplier(self._remove0))
      
      if hasattr(baseklass, "place") and callable(baseklass.place):
        baseklass.place(self)
  
  return type(classname, (buildclass,), {})
