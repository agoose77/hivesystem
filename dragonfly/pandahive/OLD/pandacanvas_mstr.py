import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *

try:
  from panda3d.core import NodePath, TextNode
  import panda3d
except ImportError:
  panda3d = None  


class pandacanvas_mstr(object):
  def _scale(self, tnode, node, x, y, sizex, sizey):
    top, bottom = tnode.getTop(), tnode.getBottom()
    w,h = tnode.getWidth(), top-bottom
    scalex = 0    
    if w > 0: scalex = sizex/w
    scaley = 0
    if h > 0: scaley = sizey/h    
    if self.aspect:
      scalex = min(scalex,scaley)
      scaley = scalex
    node.setScale(scalex,1,-scaley)
    node.setPos(x-0.5*w*scalex,0,y+1*top*scaley)
  
  def draw_mstr(self, mstr, box, identifier = "", parameters=None):
    self.aspect = True
    if box.mode == "pixels":
      parent2d = self.get_parent_pixel2d()
    elif box.mode == "standard":
      parent2d = self.get_parent_render2d()
    elif box.mode == "aspect":
      parent2d = self.get_parent_aspect2d()
    
    tnode = TextNode(identifier)
    tnode.setText(mstr.value)
    #TODO: use more parameters
    if hasattr(parameters,"cardcolor"):
      tnode.setCardColor(*parameters.cardcolor)
      tnode.setCardAsMargin(0,0,0,0)
      tnode.setCardDecal(True)
    if hasattr(parameters,"aspect"):
      self.aspect = parameters.aspect
   
    node = NodePath(tnode)
    self._scale(tnode, node, box.x, box.y, box.sizex, box.sizey)    
    node.setBin("fixed", self.get_next_sortid())
    node.setDepthTest(False)
    node.setDepthWrite(False)        
    node.reparentTo(parent2d)
    return (mstr, node, tnode, box, parameters)
    
  def update_mstr(self, mstrobject):
    mstr, node, tnode, box, parameters = mstrobject
    tnode.setText(mstr.value)
    self._scale(tnode, node, box.x, box.y, box.sizex, box.sizey)
    #TODO: box update
    #TODO: parameter update         
    
  def remove_mstr(self, mstrobject):
    mstr, node, tnode, box, parameters = mstrobject
    node.removeNode()
    
  def place(self):    
    if panda3d is None: raise ImportError("Cannot locate Panda3D")
    
    libcontext.plugin(("canvas", "draw", "mstr"), plugin_supplier(self.draw_mstr))
    libcontext.plugin(("canvas", "update","mstr"), plugin_supplier(self.update_mstr))  
    libcontext.plugin(("canvas", "remove","mstr"), plugin_supplier(self.remove_mstr))  
  
