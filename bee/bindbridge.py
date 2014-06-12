import libcontext
from . import worker, drone

class bindbridge(drone):
  def __init__(self, bindobject):
    self.bindobject = bindobject
  def place(self):
    for binder in self.bindobject.binderinstances:
      if getattr(self.bindobject,binder.parametername) != binder.parametervalue: continue
      #print binder.parametername, binder.parametervalue, str(binder.binderdroneinstance.__beename__), tuple(binder.antennanames)
      if len(binder.antennanames):
        if binder.antennanames != ["bindname"]:
          raise TypeError("Static binder worker cannot provide bindantennas %s" % list(binder.antennanames))            
        binder.binderdroneinstance.bind(self.bindobject, bindname=self.bindobject.b_bindname)  
      else:
           binder.binderdroneinstance.bind(self.bindobject)
    s = libcontext.socketclasses.socket_supplier(lambda f:self.bindobject.startupfunctions.append(f))    
    libcontext.socket("startupfunction", s)

