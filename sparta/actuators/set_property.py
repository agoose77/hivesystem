import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *
from bee.types import stringtupleparser

class set_property(object):
    """
The set_property actuator modifies a named property
    """
    metaguiparams = {
      "type_" : "str",
      "idmode" : "str",
      "autocreate" : {"idmode" : "bound", "type_": "bool"},
    }
    @classmethod
    def form(cls, f):
        f.idmode.name = "ID mode"
        f.idmode.type = "option"
        f.idmode.options = "unbound", "bound", "fallback"
        f.idmode.optiontitles = "Unbound", "Bound", "Fallback"
        f.idmode.default = "bound"
        
        f.type_.name = "Type"
        f.type_.type = "option"        
        f.type_.options = "bool", "int", "float", "(str,identifier)", "(str,action)", "(str,keycode)", "(str,message)", "(str,property)", "(str,process)", "str", "(object,matrix)", "(object,bge)", "object", "custom"
        f.type_.optiontitles = "Bool", "Integer", "Float", "ID String", "Action String", "Key String", "Message String", "Property String", "Process ID String",  "Generic String", "Matrix Object", "BGE Object", "Generic Object", "Custom"
        f.type_.default = "bool"
    
    def __new__(cls, idmode, type_):
        assert idmode in ("bound", "unbound", "fallback"), idmode
        type_ = stringtupleparser(type_)
        class set_property(bee.worker):
            __doc__ = cls.__doc__
            trig = antenna("push", "trigger")
            prop = antenna("pull", ("str", "property"))
            propval = antenna("pull", type_)
            
            if idmode == "unbound":
                identifier = antenna("pull", ("str", "identifier"))
                
            # Name the inputs and outputs
            guiparams = {
              "trig" : {"name": "Trigger"},              
              "identifier" : {"name" : "Identifier", "fold" : True},
              "prop" : {"name" : "Property Name", "fold" : True},
              "propval" : {"name" : "Property Value"},
              "_memberorder" : ["trig", "identifier", "prop", "propval"],
            }
                
            def place(self):
                raise NotImplementedError("sparta.assessors.set_property has not been implemented yet")
        
        return set_property
