import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *
from dragonfly.keycodes import *


class keyboard(bee.worker):
    """
    The keyboard sensor reports any keyboard input during the last tick
    """

    # Which key are we listening for?
    keycode = variable(("str", "keycode"))
    parameter(keycode, "Any")

    #Are we listening for key presses or key releases?
    mode = variable("str")
    parameter(mode, "keypressed")

    #Has a key been pressed during the last tick?
    is_active = variable("bool")
    startvalue(is_active, False)
    active = output("pull", "bool")
    connect(is_active, active)

    #What is the value of the last key? 
    # It will be "" if no key has been pressed/released during the last tick
    keyvalue = variable(("str", "keycode"))
    startvalue(keyvalue, "")
    key = output("pull", ("str", "keycode"))
    connect(keyvalue, key)

    # Mark "key" as an advanced output segment, and capitalize the I/O names
    guiparams = {"key": {"advanced": True, "name": "Key"},
                 "active": {"name": "Active"},
                 "_memberorder": ["key", "active"]}

    #Upon a key event, become active on the next tick 
    #1. If we are listening for any key:
    def activate1(self, event):
        self.is_active_next = True
        #Also record the value of the key
        self.keyvalue_next = event[2]

    #2. if we are listening for a specific key:
    def activate2(self, event):
        self.is_active_next = True

    #Every tick, update the current output values to the next tick's values
    # and reset the next tick's values
    def update(self):
        self.is_active = self.is_active_next
        self.keyvalue = self.keyvalue_next
        self.is_active_next = False
        self.keyvalue_next = ""

    #Add event listeners at startup
    def set_add_listener(self, add_listener):
        self.add_listener = add_listener

    def enable(self):
        #Initialize the output values for the next tick
        self.is_active_next = False
        self.keyvalue_next = ""

        #Add a high-priority update() listener on every tick
        self.add_listener("trigger", self.update, "tick", priority=9)

        #Add an activate() listener for key events
        if self.keycode == "Any":
            activate = self.activate1
        else:
            activate = self.activate2
        self.add_listener("match_leader", activate, ("keyboard", self.mode, self.keycode))

    # Method to manipulate the parameter form as it appears in the GUI
    @classmethod
    def form(cls, f):
        f.keycode.name = "Key"
        f.keycode.options = ("Any",) + keycodes

        f.mode.advanced = True
        f.mode.name = "Sensor mode"
        f.mode.type = "option"
        f.mode.options = "keypressed", "keyreleased"
        f.mode.optiontitles = "Detect key presses", "Detect key releases"

        # Finally, declare our sockets and plugins, to communicate with the rest of the hive

    def place(self):
        #Grab the hive's function for adding listeners
        libcontext.socket(("evin", "add_listener"), socket_single_required(self.set_add_listener))
        #Make sure we are enabled at startup
        libcontext.plugin(("bee", "init"), plugin_single_required(self.enable))

        #Declare flag sockets, to declare that we require keyboard support
        # If there is no keyboard support, an error will now be raised when the hive is closed        
        libcontext.socket(("evin", ("input", "keyboard")), socket_flag())
        # If we are listening for non-ASCII keys, we need support for those keys too
        if self.keycode != "Any" and self.keycode not in asciilist:
            libcontext.socket(("evin", ("input", "keyboard", "extended")), socket_flag())

