import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *

from .blenderimage import blenderimage

class blendercanvas_image(object):
  def draw_image(self, imagefile, identifier, box, parameters=None):

    if box.mode == "pixels":
      parent2d = self.get_pixel2d()
    elif box.mode == "standard":
      parent2d = self.get_render2d()
    elif box.mode == "aspect":
      parent2d = self.get_aspect2d()

    im = blenderimage(identifier,imagefile,parameters,self.textureloader)
    
    node = im.node

    node.setPos(box.x,box.y+box.sizey,0)
    node.setScale(box.sizex,box.sizey,1)
    
    #node.setBin("fixed", self.get_next_sortid())
    #node.setDepthTest(False)
    #node.setDepthWrite(False)        
    node.reparentTo(parent2d)
    return (im,imagefile,box,parameters)  
  def update_image(self, imageobject):
    image, imagefile,box,parameters = imageobject
    #TODO: box update
    #TODO: parameter update 
    if imagefile != image.imagefile:
      image.imagefile = imagefile
      image.update_image()
  def _set_textureloader(self, textureloader):
    self.textureloader = textureloader
  def place(self):
    libcontext.plugin(("canvas", "draw0", ("object","image")), plugin_supplier(self.draw_image))
    libcontext.plugin(("canvas", "show0", ("object","image")), plugin_supplier(self.draw_image))
    libcontext.plugin(("canvas", "update0", ("object","image")), plugin_supplier(self.update_image))  
    libcontext.socket("textureloader", socket_single_required(self._set_textureloader))
