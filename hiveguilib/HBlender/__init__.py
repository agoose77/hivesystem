scalefactor = 1.5

def scalepos(pos):
  """
  Scale the position from Hivemap to Blender
  """
  return pos[0] * scalefactor, pos[1] * scalefactor

def unscalepos(pos):
  """
  Scale the position from Blender to Hivemap
  """
  return pos[0] / scalefactor, pos[1] / scalefactor

  from .Application import Application
from .MainWindow import MainWindow
from .NodeCanvas import NodeCanvas
from .StatusBar import StatusBar

def FileDialog(mode):
  raise NotImplementedError