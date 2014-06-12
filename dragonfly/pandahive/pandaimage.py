import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *
import bee

try:
  from panda3d.core import NodePath
  from panda3d.core import CardMaker
  from pandac.PandaModules import TransparencyAttrib
  import panda3d
except ImportError:
  panda3d = None

class canvasdrone_baseclass(object):
  def _set_loader(self,get_loader):
    self.get_loader = get_loader    
  def place(self):
    libcontext.socket(("panda", "noderoot", "loader"), socket_single_required(self._set_loader))

class pandaimage(object):
  def __init__(self, canvasdrone, image, identifier, parentnode, parameters):
    if panda3d is None: raise ImportError("Cannot locate Panda3D")  
    self.canvasdrone = canvasdrone
    self.node = None
    self.image = None
    self._draw(image, identifier, parentnode, parameters)
  def update(self, image, identifier, parentnode, parameters):
    self._draw(image, identifier, parentnode, parameters)
  def remove(self):
    pass  

  def _draw(self, image, identifier, parentnode, parameters):
    if self.node is not None: self.node.removeNode()
    if image != self.image:
      self.tex = self.canvasdrone.get_loader().loadTexture(image)
      self.image = image
    cm = CardMaker(identifier)
    node = NodePath(cm.generate())
    node.setTexture(self.tex)
    if parameters is not None:
      if hasattr(parameters, "transparency") and parameters.transparency == True:
        node.setTransparency(TransparencyAttrib.MAlpha) 
    node.setScale(1,1,-1)
    node.reparentTo(parentnode)
    
    
