import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *

from .bglnode import bglnode

has_bgl = False
try:
  from bgl import *
  import blf
  has_bgl = True
except ImportError:
  pass

class textnode(bglnode):
  def draw(self):
    glColor3f(1,1,1)
    glPushMatrix()
    glTranslatef(*self.pos)
    glScalef(*self.scale)    
    texts = self.text.split('\n')
    #print(texts)
    for i, txt in enumerate(texts):
       blf.position(0, 0, 0, 0)
       glScalef(1,-1,-1)
       blf.size(0,100,72)    
       blf.draw(0, txt.replace('\t', '    '))
    glPopMatrix()

class blendercanvas_mstr(object):
  
  def draw_mstr(self, mstr, identifier, box, parameters=None):
    self.aspect = True
    if box.mode == "pixels":
      parent2d = self.get_pixel2d()
    elif box.mode == "standard":
      parent2d = self.get_render2d()
    elif box.mode == "aspect":
      parent2d = self.get_aspect2d()
    
    node = textnode(identifier)
    #TODO: use more parameters
    #if hasattr(parameters,"cardcolor"):
    #  tnode.setCardColor(*parameters.cardcolor)
    #  tnode.setCardAsMargin(0,0,0,0)
    #  tnode.setCardDecal(True)
    #if hasattr(parameters,"aspect"):
    #  self.aspect = parameters.aspect
   
    node.setPos(box.x-0.5*box.sizex,box.y+box.sizey,0)
    node.setScale(box.sizex,box.sizey,1)
    node.reparentTo(parent2d)
    ret = (mstr, node, box, parameters)
    self.update_mstr(ret)
    return ret
    
  def update_mstr(self, mstrobject):
    mstr, node, box, parameters = mstrobject
    node.text = mstr.value
    blf.size(0,100,72)
    w,h = blf.dimensions(0, node.text)    
    #add a little margin...
    margin = 55
    w += margin; h += margin
    
    scalex = 0
    if w > 0: scalex = box.sizex/w
    scaley = 0
    if h > 0: scaley = box.sizey/h
    if self.aspect:
      scalex = min(scalex,scaley)
      scaley = scalex      
    node.setScale(scalex, scaley, 1)
    node.setPos(box.x-0.5*(w-margin)*scalex,box.y+(h-0.5*margin)*scaley,0)    
    #TODO: box update
    #TODO: parameter update     
    
    return True
  def place(self):    
    libcontext.plugin(("canvas", "draw0", "mstr"), plugin_supplier(self.draw_mstr))
    libcontext.plugin(("canvas", "show0", "mstr"), plugin_supplier(self.draw_mstr))
    libcontext.plugin(("canvas", "update0","mstr"), plugin_supplier(self.update_mstr))  
  
  
