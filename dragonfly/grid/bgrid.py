import array, copy

#Two-dimensional binary grid class

class bgrid(object):
  minx = 9999999
  maxx = -9999999
  miny = 9999999
  maxy = -9999999
  
  _masks = [1,2,4,8,16,32,64,128]
  _false_masks = [255-a for a in _masks]
  
  def __init__(self,minx=None,maxx=None,miny=None,maxy=None,values=[]):
    """
    'values' is a list of (x,y) tuples
    """  
    if isinstance(minx, bgrid):
      grid = minx
      self.set(grid)
      return

    if len(values) == 0:
      assert minx is not None, minx
      assert maxx is not None, maxx
      assert minx is not None, miny
      assert maxy is not None, maxy    
    for x,y in values:
      if self.minx is None or x < self.minx: self.minx = int(x)
      if self.maxx is None or x > self.maxx: self.maxx = int(x)
      if self.miny is None or y < self.miny: self.miny = int(y)
      if self.maxy is None or y > self.maxy: self.maxy = int(y)
    
    if minx is not None: self.minx = int(minx)
    if maxx is not None: self.maxx = int(maxx)
    if miny is not None: self.miny = int(miny)
    if maxy is not None: self.maxy = int(maxy)
    #print("MINX", self.minx, "MAXX", self.maxx)
    #print("MINY", self.miny, "MAXY", self.maxy)
    assert self.minx <= self.maxx, (self.minx,self.maxx)
    assert self.miny <= self.maxy, (self.miny,self.maxy)
    
    self._stride = int(int((self.maxy-self.miny+1)+7)/8)
    self.size = self._stride*int(self.maxx-self.minx+1)    
    self.set_values(values)
       
  def set_true(self,x,y):
    if x < self.minx or x > self.maxx: raise ValueError(x)
    if y < self.miny or y > self.maxy: raise ValueError(y)
    if x - self.minx != int(x - self.minx): raise ValueError(x)
    if y - self.miny != int(y - self.miny): raise ValueError(y)    
    xpos = x-self.minx
    ypos = int((y-self.miny)/8)
    ypos2 = (y-self.miny) % 8
    #print("MINX", self.minx, "MAXX", self.maxx)
    #print("MINY", self.miny, "MAXY", self.maxy)
    #print("POS", xpos, ypos, self._stride, self.size, self._stride*int(self.maxx-self.minx+1))
    byte = self._data[xpos*self._stride+ypos]
    byte = byte | self._masks[ypos2]
    self._data[xpos*self._stride+ypos] = byte

  def set_false(self,x,y):
    if x < self.minx or x > self.maxx: raise ValueError(x)
    if y < self.miny or y > self.maxy: raise ValueError(y)
    if x - self.minx != int(x - self.minx): raise ValueError(x)
    if y - self.miny != int(y - self.miny): raise ValueError(y)    
    xpos = x-self.minx
    ypos = int((y-self.miny)/8)
    ypos2 = (y-self.miny) % 8
    byte = self._data[xpos*self._stride+ypos]
    byte = byte & self._false_masks[ypos2]
    self._data[xpos*self._stride+ypos] = byte
  
  def get_value(self,x,y):
    if x < self.minx or x > self.maxx: raise ValueError(x)
    if y < self.miny or y > self.maxy: raise ValueError(y)  
    if x - self.minx != int(x - self.minx): raise ValueError(x)
    if y - self.miny != int(y - self.miny): raise ValueError(y)        
    xpos = x-self.minx
    ypos = int((y-self.miny)/8)
    ypos2 =(y-self.miny) % 8
    byte = self._data[xpos*self._stride+ypos]
    return ((byte & self._masks[ypos2]) > 0)
  
  def set(self, grid):
    self.minx = grid.minx
    self.maxx = grid.maxx
    self.miny = grid.miny
    self.maxy = grid.maxy
    self.size = grid.size
    self._stride = grid._stride
    self._data = copy.copy(grid._data)
    
  def set_values(self, values):    
    self._data = array.array('B',(0,)*self.size)  
    for x,y in values:
      self.set_true(x,y)
  
  def get_values(self):
    values = []
    xpos = 0    
    for x in range(self.minx, self.maxx+1):
      ypos,ypos2 = 0,0
      byte = self._data[xpos*self._stride]
      for y in range(self.miny, self.maxy+1):        
        if (byte & self._masks[ypos2]): values.append((x,y))
        ypos2 += 1
        if (ypos2 == 8):
          ypos2 = 0
          ypos += 1
          byte = self._data[xpos*self._stride+ypos]  
      xpos += 1
    return tuple(values)
    
  def merge(self, grid):
    assert isinstance(grid, bgrid)
    cminx = max(grid.minx,self.minx)
    cmaxx = min(grid.maxx,self.maxx)
    cminy = max(grid.miny,self.miny)
    cmaxy = min(grid.maxy,self.maxy)
    for x in range(cminx,cmaxx+1):
      for y in range(cminy,cmaxy+1):
        if grid.get_value(x,y): 
          self.set_true(x,y)
        
  def overlap(self, grid):
    assert isinstance(grid, bgrid)
    cminx = max(grid.minx,self.minx)
    cmaxx = min(grid.maxx,self.maxx)
    cminy = max(grid.miny,self.miny)
    cmaxy = min(grid.maxy,self.maxy)
    for x in range(cminx,cmaxx+1):
      for y in range(cminy,cmaxy+1):
        if grid.get_value(x,y) and self.get_value(x,y): return True
    return False

  def rotate(self,times):
    times = times % 4
    if times == 0: return
    values = self.get_values()
    centerx = (self.minx+self.maxx)/2.0
    centery = (self.miny+self.maxy)/2.0
    if int(centerx) == centerx: centery = int(centery)
    if int(centery) == centery: centerx = int(centerx)
    values = [(x-centerx,y-centery) for x,y in values]
    minx = self.minx - centerx
    maxx = self.maxx - centerx
    miny = self.miny - centery
    maxy = self.maxy - centery
    if times == 1: #counter-clockwise
      values = [(-y,x) for x,y in values]
      dminx, dminy = -maxy, minx
      dmaxx, dmaxy = -miny, maxx
    elif times == 2: #180 degrees 
      values = [(-x,-y) for x,y in values]
      dminx, dminy = -maxx, -maxy
      dmaxx, dmaxy = -minx, -miny
    elif times == 3: #clockwise
      values = [(y,-x) for x,y in values]
      dminx, dminy = miny, -maxx
      dmaxx, dmaxy = maxy, -minx
    values = [(int(x+centerx),int(y+centery)) for x,y in values] 
    self.minx = int(dminx + centerx)
    self.maxx = int(dmaxx + centerx)
    self.miny = int(dminy + centery)
    self.maxy = int(dmaxy + centery)
    self._stride = int(int((self.maxy-self.miny+1)+7)/8)    
    self.size = self._stride*int(self.maxx-self.minx+1)    
    self.set_values(values)

  def translate(self,x,y):
    self.minx += int(x)
    self.maxx += int(x)
    self.miny += int(y)
    self.maxy += int(y)
  def __str__(self):
    return str(self.get_values()) 
  
  
