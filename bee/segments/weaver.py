from .. import types
from ._runtime_segment import runtime_weaver

class weaver(object):
  identifier = None
  def __init__(self, type, *inputs):
    self.type = types.typeclass(type).get_tuple()
    if len(self.type) != len(inputs):
      raise TypeError("Weaver is declared as a tuple of %d inputs, but was initialized with only %d" % (len(self.type), len(inputs)))
    self.inputs = []
    for inp in inputs:
      self.inputs.append(types.connection_outputclass(inp))
    self._connection_output = []
      
    self.bound = True    
    for inp, typ in zip(self.inputs, self.type):
      refetyp = types.mode_type("pull", typ)
      if inp.bound == True:
        inptyp = inp.value.connection_output_type()
        inptyp = types.mode_type(*inptyp)      
        if inptyp != refetyp:
          raise TypeError("Weaver input type should be (%s, %s), is (%s, %s)" % \
          (refetyp.mode.value, refetyp.type.value, inptyp.mode.value, inptyp.type.value))
      else:
        self.bound = False

  def typetest(self):    
    for inp, typ in zip(self.inputs, self.type):
      refetyp = types.mode_type("pull", typ)
      inptyp = inp.value.connection_output_type()
      inptyp = types.mode_type(*inptyp)      
      if inptyp != refetyp:
        raise TypeError("Weaver input type should be (%s, %s), is (%s, %s)" % \
        (refetyp.mode.value, refetyp.type.value, inptyp.mode.value, inptyp.type.value))
        
  def bind(self, classname, dic):
    if not self.bound:
      for inp in self.inputs:
        if not inp.bound: inp.bind(classname, dic)
      self.bound = True
      self.typetest()

  def connection_output_type(self):
    return "pull", self.type
  def connection_output(self, connection):
    self._connection_output.append(connection)    

  def connect(self, identifier):
    class weaver_proxy:
      def __init__(self, identifier):
        self.identifier = identifier
    self.identifier = "weaver-"+identifier    
    for inr,inp in enumerate(self.inputs):
      inp.value.connection_output(weaver_proxy(self.identifier+":"+str(inr+1)))
  
  def build(self, segmentname):
    dic = {
      "segmentname":segmentname, 
      "identifier": self.identifier,       
      "_inputs":self.inputs,
      "connection_output":self._connection_output,
    }
    return type("runtime_weaver:"+segmentname, (runtime_weaver,), dic)
  
