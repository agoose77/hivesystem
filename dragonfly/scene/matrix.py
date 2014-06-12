class matrix(object):
  _matrixview = None
  def set_matrixview(self, matrixview):
    self._matrixview = matrixview  
  
  formats = ("AxisSystem", "NodePath", "Blender")
  def __init__(self, wrapmatrix, format):
    assert format in self.formats
    assert wrapmatrix is not None
    self._wrapmatrix = wrapmatrix
    self._format = format
    
  def get_proxy(self, format):
    assert format in self.formats
    #if format == self._format: return self._wrapmatrix
    if (format, self._format) == ("NodePath", "NodePath"):
      from .matrix_panda import nodepath_wraps_nodepath
      proxy = nodepath_wraps_nodepath(self._wrapmatrix)    
    elif (format, self._format) == ("AxisSystem", "NodePath"): 
      from .matrix_spyder import axissystem_wraps_nodepath
      proxy = axissystem_wraps_nodepath(self._wrapmatrix)
    elif (format, self._format) == ("NodePath", "AxisSystem"):
      from .matrix_panda import nodepath_wraps_axissystem
      proxy = nodepath_wraps_axissystem(self._wrapmatrix)    
    elif (format, self._format) == ("NodePath", "Blender"):
      from .matrix_panda import nodepath_wraps_blender
      proxy = nodepath_wraps_blender(self._wrapmatrix)    
    elif (format, self._format) == ("AxisSystem", "Blender"):
      from .matrix_spyder import axissystem_wraps_blender
      proxy = axissystem_wraps_blender(self._wrapmatrix)    
    else: 
      raise Exception("Not implemented: %s wraps %s" % (format, self._format))
    proxy.set_matrixview(self._matrixview)
    return proxy
  def get_copy(self, format):
    assert format in self.formats
    if (format, self._format) == ("AxisSystem", "AxisSystem"): 
      return type(self._wrapmatrix)(self._wrapmatrix)
    elif (format, self._format) == ("NodePath", "NodePath"): 
      ret = type(self._wrapmatrix)("")      
      ret.setMat(self._wrapmatrix.getMat())
      return ret
    elif (format, self._format) == ("AxisSystem", "NodePath"):
      from .matrix_spyder import mat4_to_axissystem
      return mat4_to_axissystem(self._wrapmatrix.getMat())
    elif (format, self._format) == ("AxisSystem", "Blender"):
      from .matrix_spyder import blender_to_axissystem
      return blender_to_axissystem(self._wrapmatrix.getMat())
    elif (format, self._format) == ("NodePath", "AxisSystem"):
      from .matrix_panda import axissystem_to_mat4
      ret = type(self._wrapmatrix)()
      mat = axissystem_to_mat4(self._wrapmatrix.getMat())
      ret.setMat(mat)
      return ret
    elif (format, self._format) == ("NodePath", "Blender"):
      from .matrix_panda import blender_to_nodepath
      return blender_to_nodepath(self._wrapmatrix.getMat())
    else: 
      raise TypeError("Not implemented: %s to %s" % (self._format, format))
  
  def get_view(self, view, secondmatrix=None):
    assert self._matrixview is None
    from .matrixview import matrixview    
    return matrixview(self, view, secondmatrix)