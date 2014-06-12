import libcontext, bee
from bee.segments import *
from bee.types import stringtupleparser

class push_buffer(object):
    """
    The push buffer holds a single value
    Whenever the buffer is triggered, the value is pushed out
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
        class push_buffer(bee.worker):    
            __doc__ = cls.__doc__
            
            # Implementation
            inp = antenna("push", type_)
            value_ = buffer("push",type_)
            outp = output("push", type_)
            connect(inp, value_)
            connect(value_, outp)
            trig = antenna("push", "trigger")
            trigger(trig, value_)
            parameter(value_)
                            
            @staticmethod
            def form(f):
                f.value_.name = "Value"
                
            guiparams = {
              "inp" : {"name": "Input"},
              "outp" : {"name": "Output"},
              "trig" : {"name": "Trigger"},
              "_memberorder" : ["trig", "inp", "outp"],
            }
                              
        return push_buffer
    