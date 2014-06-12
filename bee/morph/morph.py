from ..pin import pinworker, inputpin, outputpin
from ..hivemodule import appcontext
from ..drone import drone
from .dockedmorph import dockedmorph
import libcontext

class morph_app(drone):
  def __init__(self):
    self.active = False
    self.morphs = {}
  def _set_mediator(self, mediator):
    self.mediator = mediator

  def _validate_dock(self, slotname, morph):
    assert slotname in self.parent.slots, slotname
    slot = self.parent.slots[slotname]
    slotinputs, slotoutputs = slot
    inputs = []
    outputs = []
    for n,bee in (morph.bees):
      if not hasattr(bee, "bee"): continue    
      if not hasattr(bee.bee, "__workerclass__"): continue
      b = bee.bee.__workerclass__
      pclass, pmode, ptype = b.__pinclass__, b.__pinmode__, b.__pintype__
      if pclass == inputpin: inputs.append((n,bee.bee,pmode,ptype))
      elif pclass == outputpin: outputs.append((n,bee.bee,pmode,ptype))
    assert len(inputs) == len(slotinputs), (slotname, len(inputs), len(slotinputs))
    assert len(outputs) == len(slotoutputs), (slotname, len(outputs), len(slotoutputs))

    ret_inp, ret_outp = [], []
    for slotinp, inp in zip(slotinputs, inputs):
      n,pin,pmode,ptype = inp
      if ptype != slotinp: raise TypeError("Inputpin %s is of type '%s', must be '%s'" % (n,ptype,slotinp))
      ret_inp.append(pin)
    for slotoutp, outp in zip(slotoutputs, outputs):
      n,pin,pmode,ptype = outp
      if ptype != slotoutp: raise TypeError("Outputpin %s is of type '%s', must be '%s'" % (n,ptype,slotoutp))
      ret_outp.append(pin)

    return ret_inp, ret_outp
    
  def dock(self, slotname, morph):  
    #TODO: break all existing pin connections of the docked morph
    inputs, outputs = self._validate_dock(slotname, morph)
    self.morphs[slotname] = dockedmorph(morph,self.mediator,inputs,outputs)

  def undock(self, slotname):
    self.morphs[slotname].undock()
    del self.morphs[slotname]
    
  def place(self):
    if not hasattr(self, "parent"): return #KLUDGE
    p = libcontext.pluginclasses.plugin_single_required(self.parent)
    libcontext.import_plugin(self.parent.parent.context, ("pin","mediator"))
    libcontext.import_socket(self.parent.parent.context, ("pin","run"))
    libcontext.import_socket(self.parent.parent.context, ("pin","push_input")) 
    libcontext.import_socket(self.parent.parent.context, ("pin","pull_input"))
    libcontext.import_socket(self.parent.parent.context, ("pin","push_output")) 
    libcontext.import_socket(self.parent.parent.context, ("pin","pull_output"))

    libcontext.plugin(("pin","run"), p)

    s = libcontext.socketclasses.socket_single_required(self._set_mediator)
    libcontext.socket(("pin","mediator"), s)

class morph(pinworker):
  slots = {}
  _hivecontext = appcontext(morph_app)  
  def run(self): 
    raise Exception("You must override the run() method of a morph!")

del morph_app
