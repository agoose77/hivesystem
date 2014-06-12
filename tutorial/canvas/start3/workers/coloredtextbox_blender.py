#try to import bgl and blf, but delay exceptions until the class is actually used
has_bgl = False
try:
  from bgl import *
  import blf
  has_bgl = True
except ImportError:
  pass

#coloredtextbox class: this will be converted to a canvas drone using "build_canvasdrone"  
class coloredtextbox(object):
  #obligatory argument list  for __init__: canvasdrone, object, identifier, parameters 
  def __init__(self, canvasdrone, ctb, identifier, parameters):
    if not has_bgl: raise ImportError("Cannot import bgl")
    from dragonfly.canvas import box2d
    if identifier is None: identifier = ""
    box = box2d(ctb.posx,ctb.posy,ctb.sizex,ctb.sizey,ctb.sizemode)
    self.pnode = canvasdrone._get_parent_bglnode(identifier, box)
    #register self as a child of pnode: pnode will now invoke self.draw() every frame
    self.pnode.children = [self]
    self.update(ctb,identifier,parameters)  
  #obligatory method "update". Argument list: object, identifier, parameters   
  def update(self, ctb, identifier, parameters):
    self.ctb = ctb
    self.textcolor = self.ctb.textcolor
    self.boxcolor = self.ctb.boxcolor
    self.text = self.ctb.text
    self._scale()
  #obligatory method "remove"
  def remove(self):
    if self.pnode is not None:
      self.pnode.removeNode()
      self.pnode = None
  def _scale(self):
    blf.size(0,100,72)
    w,h = blf.dimensions(0, self.text)    
    #add a little margin...
    margin = 55
    w += margin; h += margin
    
    scalex = 0
    if w > 0: scalex = 1.0/w
    scaley = 0
    if h > 0: scaley = 1.0/h
    self.scale = (scalex, scaley, 1)
    self.pos = (0.5-0.5*(w-margin)*scalex,-0.5*(h-margin)*scaley,0)    
  def draw(self):
    r,g,b,a = self.boxcolor
    glColor4f(r,g,b,a)
    glBegin(GL_QUADS)
    glVertex2f(0,0)
    glVertex2f(0,-1)
    glVertex2f(1,-1)
    glVertex2f(1,0)
    glEnd()
    r,g,b,a = self.textcolor
    glColor4f(r,g,b,a)
    glPushMatrix()
    glTranslatef(*self.pos)
    glScalef(*self.scale)
    txt = self.text
    blf.position(0, 0, 0, 0)
    glScalef(1,-1,-1)
    blf.size(0,100,72)    
    blf.draw(0, txt.replace('\t', '    '))
    glPopMatrix()
    glColor4f(1,1,1,1)
  
import bee
from dragonfly.canvas import canvasdrone
from dragonfly.blenderhive import build_canvasdrone

coloredtextbox_blender = build_canvasdrone(
  wrappedclass = coloredtextbox, 
  classname = "coloredtextbox_blender",
  drawshow = "show",
  drawshowtype = ("object", "coloredtextbox"),
  baseclass = canvasdrone
)  

