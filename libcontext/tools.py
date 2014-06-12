class lazyattr(object):
  """
  Supply an object and an attribute that the object doesn't have yet
  The lazyattr will be a wrapper around that object  
  """
  def __init__(self, obj, attr):
    self._obj = obj
    self._attr = attr
    self._wrapped = None
  def __getattr__(self, attr):
    if self._wrapped is None: self._wrapped = getattr(self._obj, self._attr)
    return getattr(self._wrapped, attr)
