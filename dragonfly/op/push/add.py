from ._template import _template

class add(object):
  metaguiparams = {"type":"type"}
  def __new__(cls,type):    
    types = {"int":int, "float":float, "str":str}  
    startvaluedict = {"int":0, "float":0, "str":""}  
    assert type in types    
    ret = _template(
      op = types[type].__add__, 
      inptypes = (type, type), 
      startvalues = (startvaluedict[type],startvaluedict[type]), 
      outptypes = (type,), 
    )
    ret.guiparams["__beename__"] = "add"
    return ret
