import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *

from .blenderbgrid import blenderbgrid
from .bglnode import bglnode

class blendercanvas_bgrid(object):
  def draw_bgrid(self, bgrid, identifier, box, parameters=None):
    
    if box.mode == "pixels":
      parent2d = self.get_pixel2d()
    elif box.mode == "standard":
      parent2d = self.get_render2d()
    elif box.mode == "aspect":
      parent2d = self.get_aspect2d()
    
    blendergrid = blenderbgrid(identifier,bgrid,parameters)
    #TODO: use more parameters
    
    node = bglnode(identifier+"-pivot")
    blendergrid.node.reparentTo(node)
    node.setPos(box.x,box.y+box.sizey,0)
    node.setScale(box.sizex,box.sizey,1)
    node.reparentTo(parent2d)
    return (node, blendergrid,box,parameters)     
  def update_bgrid(self, gridobject):
    node, blendergrid,box,parameters = gridobject
    #TODO: box update
    #TODO: parameter update 
    #TODO:  blendergrid.update_parameters(parameters)
    blendergrid.update(node)
  def place(self):
    libcontext.plugin(("canvas", "draw0", ("object","bgrid")), plugin_supplier(self.draw_bgrid))
    libcontext.plugin(("canvas", "show0", ("object","bgrid")), plugin_supplier(self.draw_bgrid))
    libcontext.plugin(("canvas", "update0", ("object","bgrid")), plugin_supplier(self.update_bgrid))  
  
  
