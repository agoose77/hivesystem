import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *

try:
  from panda3d.core import NodePath
  import panda3d
except ImportError:
  panda3d = None  

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

    def get_parent_render2d(self):
      if self._render2d is None:
        self._render2d = self.get_render2d().attachNewNode("render2d-pandacanvas")
        self._render2d.setPos(-1,0,1)
        self._render2d.setScale(2,1,-2)
      return self._render2d

    def get_parent_aspect2d(self):
      if self._aspect2d is None:
        self._aspect2d = self.get_aspect2d().attachNewNode("aspect2d-pandacanvas")
        x,y = self.canvas_size()
        self._aspect2d.setPos(-float(x)/y,0,1)
        self._aspect2d.setScale(2,1,-2)
      return self._aspect2d

    def get_parent_pixel2d(self):
      if self._pixel2d is None:
        self._pixel2d = self.get_pixel2d().attachNewNode("pixel2d-pandacanvas")
        self._pixel2d.setScale(1,1,-1)
      return self._pixel2d

    def get_parent2d(self, box):  
      if box.mode == "pixels":
        parent2d = self.get_parent_pixel2d()
      elif box.mode == "standard":
        parent2d = self.get_parent_render2d()
      elif box.mode == "aspect":
        parent2d = self.get_parent_aspect2d()
      else:
        raise ValueError(box.mode)  
      return parent2d  

    def _get_parent_nodepath(self, identifier, box):
      parent2d = self.get_parent2d(box)
      node = NodePath(identifier+"-pivot")
      node.setPos(box.x,0,box.y+box.sizey)
      node.setScale(box.sizex,1,box.sizey)
      node.setBin("fixed", self._get_next_sortid())
      node.setDepthTest(False)
      node.setDepthWrite(False)        
      node.reparentTo(parent2d)      
      return node
    
    def get_canvas_size(self, canvas_sizefunc):
      self.canvas_size = canvas_sizefunc

    def _draw(self, obj, identifier, box, parameters=None):    
      self._nodes[identifier] = self._get_parent_nodepath(identifier, box)
      self.drawshowinstances[identifier] = wrappedclass(self, obj, identifier, self._nodes[identifier], parameters)
      self._boxes[identifier] = box
    def _show(self, obj, identifier, parameters=None):    
      self.drawshowinstances[identifier] = wrappedclass(self, obj, identifier, parameters)
    def _update_draw(self, obj, identifier, box, parameters=None):    
      if box is not self._boxes[identifier]:
        newnode = self._get_parent_nodepath(identifier, box)
        ret = self.drawshowinstances[identifier].update(obj, identifier, newnode, parameters)
        if ret is not None: self.drawshowinstances[identifier] = ret
        self._nodes[identifier].removeNode()
        self._nodes[identifier] = newnode
        self._boxes[identifier] = box
      else:
        ret = self.drawshowinstances[identifier].update(obj, identifier, self._nodes[identifier], parameters)
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
              
    def place(self):
      if panda3d is None: raise ImportError("Cannot locate Panda3D")

      libcontext.socket(("panda", "noderoot", "pixel2d"), socket_single_required(self._set_pixel2d))
      libcontext.socket(("panda", "noderoot", "render2d"), socket_single_required(self._set_render2d))
      libcontext.socket(("panda", "noderoot", "aspect2d"), socket_single_required(self._set_aspect2d))
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
