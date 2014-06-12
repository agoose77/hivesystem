import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class trigger(bee.worker):
    """
    The trigger processor becomes True for the rest of the tick after it receives a trigger 
    """

    # Has a trigger been received during the last tick?
    is_active = variable("bool")
    startvalue(is_active, False)
    active = output("pull", "bool")
    connect(is_active, active)

    # When we receive a trigger, become active
    trig = antenna("push", "trigger")

    @modifier
    def activate(self):
        self.is_active = True

    trigger(trig, activate)

    # Capitalize the I/O names    
    guiparams = {
        "active": {"name": "Active"},
        "trig": {"name": "Trigger"},
        "_memberorder": ["trig", "active"],
    }

    # Every tick, set the current output value to False
    def deactivate(self):
        self.is_active = False

    # Add event listeners at startup
    def set_add_listener(self, add_listener):
        self.add_listener = add_listener

    def enable(self):
        # Add a high-priority deactivate() listener on every tick
        self.add_listener("trigger", self.deactivate, "tick", priority=9)

    # Finally, declare our sockets and plugins, to communicate with the rest of the hive
    def place(self):
        # Grab the hive's function for adding listeners
        libcontext.socket(("evin", "add_listener"), socket_single_required(self.set_add_listener))
        #Make sure we are enabled at startup
        libcontext.plugin(("bee", "init"), plugin_single_required(self.enable))
    
      
      
