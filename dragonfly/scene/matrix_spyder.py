from Spyder import Coordinate, AxisSystem

def mat4_to_axissystem(mat):
  ret = AxisSystem.empty()  
  ret.x = Coordinate(list(mat.getRow(0))[:3])
  ret.y = Coordinate(list(mat.getRow(1))[:3])
  ret.z = Coordinate(list(mat.getRow(2))[:3])
  ret.origin = Coordinate(list(mat.getRow(3))[:3])
  return ret

def blender_to_axissystem(mat):
  ret = AxisSystem.empty()  
  #TODO: test if it is fine with row-major, column-major, etc.
  # also, what is the difference between Orientation and localOrientation?
  x = Coordinate(mat.localOrientation[0])
  y = Coordinate(mat.localOrientation[1])
  z = Coordinate(mat.localOrientation[2])
  """
  x = Coordinate(mat.orientation[0])
  y = Coordinate(mat.orientation[1])
  z = Coordinate(mat.orientation[2])
  """
  """
  ret.x = x
  ret.y = y
  ret.z = z
  """
  ret.x = Coordinate(x.x,y.x,z.x)
  ret.y = Coordinate(x.y,y.y,z.y)
  ret.z = Coordinate(x.z,y.z,z.z)
  
  
  ret.origin = Coordinate(mat.localPosition)
  #ret.origin = Coordinate(mat.position)
  return ret


class axissystem_wraps_nodepath(object):
  _matrixview = None
  def set_matrixview(self, matrixview):
    self._matrixview = matrixview  

  def __init__(self, nodepath):
    self._nodepath = nodepath
    axis = mat4_to_axissystem(nodepath.getMat())
    self._axis = axis
  def __getattr__(self, attr):
    return getattr(self._axis, attr)
  def __str__(self):
    axis = AxisSystem(self.origin, self.x,self.y,self.z)
    return axis.__str__()
  def set_axissystem(self, axis):
    self._axis = axis
  def commit(self):
    from .matrix_panda import axissystem_to_mat4
    axis = AxisSystem(self.origin, self.x,self.y,self.z)
    self._nodepath.setMat(axissystem_to_mat4(axis))
    if self._matrixview is not None:
      self._matrixview(self._nodepath)
    
class axissystem_wraps_blender(object):
  _matrixview = None
  def set_matrixview(self, matrixview):
    self._matrixview = matrixview  

  def __init__(self, blender):
    self._blender = blender    
    axis = blender_to_axissystem(blender)
    self._axis = axis
  def __getattr__(self, attr):
    return getattr(self._axis, attr)
  def __str__(self):
    axis = AxisSystem(self.origin, self.x,self.y,self.z)
    return axis.__str__()
  def set_axissystem(self, axis):
    self._axis = axis
  def commit(self):
    from .matrix_blender import axissystem_to_blender
    axis = AxisSystem(self.origin, self.x,self.y,self.z)
    axissystem_to_blender(axis, self._blender)
    if self._matrixview is not None:
      self._matrixview(self._blender)
