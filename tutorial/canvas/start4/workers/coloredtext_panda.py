#try to import Panda3D, but delay exceptions until the class is actually used
try:
  from panda3d.core import NodePath, TextNode
  import panda3d
except ImportError:
  panda3d = None  

#coloredtext class: this will be converted to a canvas drone using "build_canvasdrone"  
class coloredtext(object):
  #obligatory argument list  for __init__: canvasdrone, object, identifier, parentnode, parameters 
  def __init__(self, canvasdrone, ctb, identifier, parentnode, parameters):
    if panda3d is None: raise ImportError("Cannot locate Panda3D")
    if identifier is None: identifier = ""
    self.node = None
    self._show(ctb, identifier, parentnode)
  #obligatory method "update". Argument list: object, identifier, parentnode, parameters   
  def update(self, ctb, identifier, parentnode, parameters):
    self._show(ctb, identifier, parentnode)
  #obligatory method "remove"
  def remove(self):
    pass
  def _show(self, ctb, identifier, parentnode):
    if self.node is not None: self.node.removeNode()
    tnode = TextNode(identifier)
    tnode.setText(ctb.text)
    r,g,b,a = ctb.textcolor.r/255.0, ctb.textcolor.g/255.0, ctb.textcolor.b/255.0,ctb.textcolor.a/255.0
    tnode.setTextColor(r,g,b,a)
    node = NodePath(tnode)
    self._scale(tnode, node)
    node.reparentTo(parentnode)
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
from dragonfly.canvas import canvasdrone
from dragonfly.pandahive import build_canvasdrone

coloredtext_panda = build_canvasdrone(
  wrappedclass = coloredtext, 
  classname = "coloredtext_panda",
  drawshow = "draw",
  drawshowtype = "ColoredText",
  baseclass = canvasdrone
)  

