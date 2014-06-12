from __future__ import print_function, absolute_import

class Layout(object):
  def _layout(self, name):        
    title = name.capitalize()    
    vis = True
    if name in ("workers", "segments", "drones", "bees"):
      parent, position = None, "left"
    elif name == "props":
      parent, position = None, "right"
    elif name == "spyderhive":  
      parent, position = None, "top"
    elif name == "proptabs":
      parent = "props"
      widget = "tab"            
      title = None
    elif name.startswith("props"):
      title = name[len("props-"):].capitalize()      
      if name in ("props-params", "props-metaparams"):
        parent = "props-parameters"
        widget = None
        vis = False
      else:
        parent = "proptabs"
        widget = "form"
    else:
      raise ValueError("Don't know how to layout subwindow '%s'" % name)
    
    if parent is not None:
      self.newSubWindow(parent, triggered=True)  
      win, outerwin = self._newSubWidget(name, title, widget, parent)      
    else:
      win = self._newSubWindow(title, position)
      outerwin = None
    return win, outerwin, vis
