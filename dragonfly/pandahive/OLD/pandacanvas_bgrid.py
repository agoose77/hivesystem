import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *

from .pandabgrid import pandabgrid

try:
  from panda3d.core import NodePath
  import panda3d
except ImportError:
  panda3d = None  


class pandacanvas_bgrid(object):
  def draw_bgrid(self, bgrid, box, identifier = "bgrid", parameters=None):
    
    if box.mode == "pixels":
      parent2d = self.get_parent_pixel2d()
    elif box.mode == "standard":
      parent2d = self.get_parent_render2d()
    elif box.mode == "aspect":
      parent2d = self.get_parent_aspect2d()
    
    pandagrid = pandabgrid(identifier,bgrid,parameters)
    #TODO: use more parameters
    
    node = NodePath(identifier+"-pivot")
    pandagrid.node.reparentTo(node)
    node.setPos(box.x,0,box.y+box.sizey)
    node.setScale(box.sizex,1,box.sizey)
    node.setBin("fixed", self.get_next_sortid())
    node.setDepthTest(False)
    node.setDepthWrite(False)        
    node.reparentTo(parent2d)
    pandagrid.update(node)
    return (node, pandagrid,box,parameters)         
  def update_bgrid(self, gridobject):
    node, pandagrid,box,parameters = gridobject
    #TODO: box update
    #TODO: parameter update 
    #TODO:  pandagrid.update_parameters(parameters)
    pandagrid.update(node)
  def remove_bgrid(self, gridobject):
    node, pandagrid,box,parameters = gridobject
    node.removeNode()
    
  def place(self):
    if panda3d is None: raise ImportError("Cannot locate Panda3D")
    libcontext.plugin(("canvas", "draw", ("object","bgrid")), plugin_supplier(self.draw_bgrid))
    libcontext.plugin(("canvas", "update", ("object","bgrid")), plugin_supplier(self.update_bgrid))
    libcontext.plugin(("canvas", "remove", ("object","bgrid")), plugin_supplier(self.remove_bgrid))
  
  
