has_bgl = False
try:
  from bgl import *
  has_bgl = True
except ImportError:
  pass

class bglnode(object):
  def __init__(self, identifier=None):
    self.identifier = identifier
    self.children = []
    self.parent = None
    self.pos = (0,0,0)
    self.scale = (1,1,1)
  def setPos(self, x,y,z):
    self.pos = (x,y,z)
  def setScale(self,x,y,z):
    self.scale = (x,y,z)
  def removeNode(self):
    if self.parent is not None:
      self.parent.children.remove(self)
      self.parent = None
  def reparentTo(self, parent):
    self.removeNode()
    parent.children.append(self)
    self.parent = parent
  def draw(self):
    glPushMatrix();
    glTranslatef(*self.pos)
    glScalef(*self.scale)    
    for child in self.children: child.draw()
    glPopMatrix()

   
class bgl_rendernode(bglnode):
  def draw(self):
    if not len(self.children): return
    assert has_bgl

    # Save the state
    glPushMatrix()
    glPushAttrib(GL_ALL_ATTRIB_BITS)

    # Disable depth test so we always draw over things
    # also disable culling, so that we can deal with left-hand/right hand differences
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    glDisable(GL_CULL_FACE)
    glBindTexture(GL_TEXTURE_2D, 0)
    glShadeModel(GL_SMOOTH)    

    # Setup the matrices
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, 1, 1, 0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    for child in self.children: 
      child.draw()
      
    # Reset the state
    glPopAttrib()
    glPopMatrix()
    
class bgl_pixelnode(bglnode):
  def windowsize(self):
    view_buf = Buffer(GL_INT, 4)
    glGetIntegerv(GL_VIEWPORT, view_buf)
    view = list(view_buf)
    return view[2], view[3]
  
  def draw(self):
    if not len(self.children): return
    assert has_bgl
    size = self.windowsize()

    # Save the state
    glPushMatrix()
    glPushAttrib(GL_ALL_ATTRIB_BITS)

    # Disable depth test so we always draw over things
    # also disable culling, so that we can deal with left-hand/right hand differences
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    glDisable(GL_CULL_FACE)
    glBindTexture(GL_TEXTURE_2D, 0)
    glShadeModel(GL_SMOOTH)
    
    # Setup the matrices
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, size[0], size[1], 0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    for child in self.children: 
      child.draw()
      
    # Reset the state
    glPopAttrib()
    glPopMatrix()
     
class bgl_aspectnode(bgl_pixelnode):
  def draw(self):
    if not len(self.children): return
    assert has_bgl
    size = self.windowsize()

    # Save the state
    glPushMatrix();
    glPushAttrib(GL_ALL_ATTRIB_BITS)

    # Disable depth test so we always draw over things
    # also disable culling, so that we can deal with left-hand/right hand differences
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    glDisable(GL_CULL_FACE)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Setup the matrices
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, 1, float(size[1])/size[0], 0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    for child in self.children: child.draw()
      
    # Reset the state
    glPopAttrib()
    glPopMatrix()
