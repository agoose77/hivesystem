#try to import Panda3D, but delay exceptions until the class is actually used
try:
  from panda3d.core import NodePath, TextNode
  import panda3d
except ImportError:
  panda3d = None  

#coloredtextbox class: this will be converted to a canvas drone using "build_canvasdrone"  
class coloredtextbox(object):
  #obligatory argument list  for __init__: canvasdrone, object, identifier, parameters 
  def __init__(self, canvasdrone, ctb, identifier, parameters):
    if panda3d is None: raise ImportError("Cannot locate Panda3D")
    if identifier is None: identifier = ""
    self.node = None
    self.pnode = canvasdrone._get_parent_nodepath(identifier, ctb.box)
    self._show(ctb, identifier)
  #obligatory method "update". Argument list: object, identifier, parameters   
  def update(self, ctb, identifier, parameters):
    self._show(ctb, identifier)
  #obligatory method "remove"
  def remove(self):
    if self.pnode is not None:
      self.pnode.removeNode()
      self.pnode = None
  def _show(self, ctb, identifier):
    if self.node is not None: self.node.removeNode()
    tnode = TextNode(identifier)
    tnode.setText(ctb.text)
    r,g,b,a = ctb.textcolor.r/255.0, ctb.textcolor.g/255.0, ctb.textcolor.b/255.0,ctb.textcolor.a/255.0
    tnode.setTextColor(r,g,b,a)
    r,g,b,a = ctb.boxcolor.r/255.0, ctb.boxcolor.g/255.0, ctb.boxcolor.b/255.0,ctb.boxcolor.a/255.0
    tnode.setCardColor(r,g,b,a)      
    tnode.setCardAsMargin(0,0,0,0)
    tnode.setCardDecal(True)
    node = NodePath(tnode)
    self._scale(tnode, node)
    node.reparentTo(self.pnode)
    self.node = node
  def _scale(self, tnode, node):
    top, bottom = tnode.getTop(), tnode.getBottom()
    l, r = tnode.getLeft(), tnode.getRight()
    w,h = r-l, top-bottom
    scalex = 0    
    if w > 0: scalex = 1.0/w
    scaley = 0
    if h > 0: scaley = 1.0/h    
    node.setScale(scalex,1,-scaley)
    dimx = w * scalex
    midx = (l * scalex + r * scalex) / 2.0
    dimy = h * scaley
    midy = (top * scaley + bottom * scaley) / 2.0
    node.setPos(-midx+0.5,0,midy-0.5)
  
import bee
from dragonfly.pandahive import build_canvasdrone
from dragonfly.pandahive.pandacanvas import pandacanvas

mycanvas_coloredtextbox = build_canvasdrone(
  wrappedclass = coloredtextbox, 
  classname = "mycanvas_coloredtextbox",
  drawshow = "show",
  drawshowtype = "ColoredTextBox",
  baseclass = object
)  

class mycanvas_panda(pandacanvas):
  def __init__(self):
    pandacanvas._wrapped_hive.__init__(self)  
    self.d_coloredtextbox = mycanvas_coloredtextbox()
  def place(self):   
    self.d_coloredtextbox.place()
    pandacanvas._wrapped_hive.place(self)

