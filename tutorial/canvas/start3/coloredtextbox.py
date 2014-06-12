class coloredtextbox(object):
  def __init__(self, text, textcolor, posx, posy, sizex, sizey, sizemode, boxcolor):
    self.text = text
    assert len(textcolor) == 3 or len(textcolor) == 4
    self.textcolor = tuple(textcolor)
    if len(textcolor) == 3: self.textcolor = self.textcolor + (1.0,)
    self.posx = posx
    self.posy = posy
    self.sizex = sizex
    self.sizey = sizey
    assert sizemode in ("pixels","standard","aspect")
    self.sizemode = sizemode
    assert len(boxcolor) == 3 or len(boxcolor) == 4
    self.boxcolor = tuple(boxcolor)
    if len(boxcolor) == 3: self.boxcolor = self.boxcolor + (1.0,)