import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *

class collision(object):
    """
    The collision sensor reports collisions between a specific object and all other objects
    The other objects can be filtered by material, property or identifier
    """
    metaguiparams = {
      "idmode" : "str",
      "autocreate" : {"idmode" : "bound"},
    }
    @classmethod
    def form(cls, f):
        f.idmode.name = "ID mode"
        f.idmode.advanced = True
        f.idmode.type = "option"        
        f.idmode.options = "unbound", "bound"
        f.idmode.default = "bound"
        f.idmode.optiontitles = "Unbound", "Bound"
    
    def __new__(cls, idmode):
        assert idmode in ("bound", "unbound"), idmode
        class collision(bee.worker):    
            __doc__ = cls.__doc__
            
            if idmode == "unbound":
                identifier = antenna("pull", ("str", "identifier"))
            
            #How are the collisions filtered?
            filtermode = variable("str")
            parameter(filtermode)
            
            #What is the value of the filter?
            filtervalue = antenna("pull", "str")
            
            #Has a collision event happened during the last tick?
            is_active = variable("bool")
            startvalue(is_active, False)
            active = output("pull", "bool")    
            connect(is_active, active)
            
            #What was the ID of the colliding object?
            v_collision_id = variable(("str", "identifier"))
            collision_id = output("pull", ("str", "identifier"))    
            connect(v_collision_id, collision_id)
                
            @staticmethod
            def form(f):
                f.filtermode.name = "Filter mode"
                f.filtermode.type = "option"
                f.filtermode.default = "id"
                f.filtermode.options = "material", "property", "id"
                f.filtermode.optiontitles = "By material", "By property", "By ID"
                
            guiparams = {
              "identifier" : {"name": "Identifier", "fold" : True},
              "filtervalue" : {"name" : "Filter value", "fold" : True},
              "active" : {"name": "Active"},
              "collision_id" : {"name" : "Collision ID", "advanced" : True }, 
              "_memberorder" : ["filtervalue", "identifier", "collision_id", "active"],
            }
                
            def place(self):
                raise NotImplementedError("sparta.sensors.collision has not been implemented yet")
              
        return collision
    