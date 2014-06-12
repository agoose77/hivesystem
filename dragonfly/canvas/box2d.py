def readonly(self,value):
  raise TypeError("Box2d properties are read-only")

class box2d(object):
  x = property(lambda self: self._x, readonly)
  y = property(lambda self: self._y, readonly)
  sizex = property(lambda self: self._sizex, readonly)
  sizey = property(lambda self: self._sizey, readonly)
  mode = property(lambda self: self._mode, readonly)
  
  def __init__(self, x, y,sizex,sizey,mode="pixels"):
    self._x = x
    self._y = y
    if sizex <= 0: raise ValueError(sizex)
    if sizey <= 0: raise ValueError(sizey)
    self._sizex = sizex
    self._sizey = sizey
    assert mode in ("pixels","standard","aspect")
    self._mode = mode
  def to_std(self, canvasx, canvasy):
    if self._mode == "standard": return self
    elif self._mode == "pixels": 
      xx, yy = pixels_to_std(self._x,self._y, canvasx, canvasy)
      mx, my = pixels_to_std(self._x+self._sizex,self._y+self._sizey, canvasx, canvasy)
      sizexx,sizeyy = mx-xx,my-yy
      ret = box2d(xx,yy,sizexx,sizeyy,"standard")
      return ret
    elif self._mode == "aspect": 
      xx, yy = aspect_to_std(self._x,self.y, canvasx, canvasy)
      mx, my = aspect_to_std(self._x+self._sizex,self._y+self._sizey, canvasx, canvasy)
      sizexx,sizeyy = mx-xx,my-yy
      ret = box2d(xx,yy,sizexx,sizeyy,"standard")
      return ret
    raise ValueError(self._mode)
              
def std_to_pixels(x,y,canvasx,canvasy):
  return x*canvasx,y*canvasy

def aspect_to_pixels(x,y,canvasx,canvasy):
  return x*canvasy,y*canvasy

def pixels_to_std(x,y,canvasx,canvasy):
  return float(x)/canvasx, float(y)/canvasy

def aspect_to_std(x,y,canvasx,canvasy):
  return float(x)*canvasy/canvasx, y

def sting_box2d(b):
  box = box2d(b.x,b.y,b.sizex,b.sizey,b.mode)
  return box

import spyder
spydermethod_box2d_sting = spyder.core.definemethod("sting", "Box2D", sting_box2d)