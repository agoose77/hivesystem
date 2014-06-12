class Layout(object):
  def _layout(self, name):        
    vis = True
    if name in ("workers", "segments", "drones", "bees"):
      parent = None
    elif name == "props":
      parent = None
    elif name == "spyderhive":  
      parent = None
    elif name == "proptabs":
      parent = "props"
    elif name.startswith("props"):
      if name in ("props-params", "props-metaparams"):
        parent = "props-parameters"
      else:
        parent = "proptabs"
    else:
      raise ValueError("Don't know how to layout subwindow '%s'" % name)
    
    if parent is not None:
      parentwin = self.newSubWindow(parent, triggered=True)  
      win = self._newSubWindow(name, parentwin)      
    else:
      win = self._newSubWindow(name)      
    return win
