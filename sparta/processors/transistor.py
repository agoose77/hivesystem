import libcontext, bee
from bee.segments import *
import bee.segments.transistor
from bee.types import stringtupleparser

class transistor(object):
    """
    A transistor converts pull input to push output
    Whenever the transistor is triggered, the value is pulled in and then pushed out
    """
    metaguiparams = {
      "type_" : "str",
      "autocreate" : {"type_" : "bool"},
    }
    @classmethod
    def form(cls, f):
        f.type_.name = "Type"
        f.type_.type = "option"        
        f.type_.options = "bool", "int", "float", "(str,identifier)", "(str,action)", "(str,keycode)", "(str,message)", "(str,property)", "(str,process)", "str", "(object,matrix)", "(object,bge)", "object", "custom"
        f.type_.optiontitles = "Bool", "Integer", "Float", "ID String", "Action String", "Key String", "Message String", "Property String", "Process ID String",  "Generic String", "Matrix Object", "BGE Object", "Generic Object", "Custom"
        f.type_.default = "bool"
    
    def __new__(cls, type_):
        type_ = stringtupleparser(type_)
        class transistor(bee.worker):    
            __doc__ = cls.__doc__
            
            # Implementation
            val = antenna("pull", type_)
            trans = bee.segments.transistor(type_)
            outp = output("push", type_)
            connect(val, trans)
            connect(trans, outp)
            trig = antenna("push", "trigger")
            trigger(trig, trans)
                                            
            guiparams = {
              "val" : {"name": "Value"},
              "outp" : {"name": "Output"},
              "trig" : {"name": "Trigger"},
              "_memberorder" : ["trig", "val", "outp"],
            }
                              
        return transistor
    