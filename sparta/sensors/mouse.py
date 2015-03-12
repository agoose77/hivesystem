import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class mouse(bee.worker):

    """The mouse sensor reports any mouse input during the last tick"""

    # What kind of mouse click events are we listening for?
    mode = variable("str")
    parameter(mode, "LClick")

    #Has a mouse event happened during the last tick?
    is_active = variable("bool")
    startvalue(is_active, False)
    active = output("pull", "bool")
    connect(is_active, active)

    #What are the X and Y positions?
    vx = variable("float")
    startvalue(vx, 0.0)
    x = output("pull", "float")
    connect(vx, x)
    vy = variable("float")
    startvalue(vy, 0.0)
    y = output("pull", "float")
    connect(vy, y)

    # Mark "x" and "y" as an advanced Output segment, and capitalize the I/O names
    guiparams = {
        "identifier": {"name": "Identifier", "fold": True},
        "x": {"name": "X Position", "advanced": True},
        "y": {"name": "Y Position", "advanced": True},
        "active": {"name": "Active"},
        "_memberorder": ["identifier", "x", "y", "active"],
    }

    # Method to manipulate the Parameter form as it appears in the GUI
    @staticmethod
    def form(f):
        f.mode.name = "Detection mode"
        f.mode.type = "option"
        f.mode.options = "Move", "LClick", "RClick", "LDoubleClick", "MiddleClick", "LDrag", "RDrag"
        f.mode.optiontitles = "Move", "Left Click", "Right Click", "Double Click", "Middle Click", "Left Button Drag", "Right Button Drag"

    #Add event listeners at startup
    def set_add_listener(self, add_listener):
        self.add_listener = add_listener

    def set_coords(self, event):
        self.vx, self.vy = event[2]

    #2. if we are listening for a specific key:
    def activate(self, event):
        self.is_active_next = True

    def update(self):
        self.is_active = self.is_active_next
        self.is_active_next = False

    def enable(self):
        #Initialize the Output values for the next tick
        self.is_active_next = False

        #Add a high-priority update() listener on every tick
        self.add_listener("trigger", self.update, "tick", priority=9)

        #Add an activate() listener for mouse events
        self.add_listener("match_leader", self.activate, ("mouse", self.mode))
        #Add a listener for mouse coordinates (from mouse move)
        self.add_listener("match_leader", self.set_coords, ("mouse", "move"))

    # Finally, declare our sockets and plugins, to communicate with the rest of the hive
    def place(self):
        #Grab the hive's function for adding listeners
        libcontext.socket(("evin", "add_listener"), socket_single_required(self.set_add_listener))
        #Make sure we are enabled at startup
        libcontext.plugin(("bee", "init"), plugin_single_required(self.enable))
        #Declare flag sockets, to declare that we require mouse support
        # If there is no mouse support, an error will now be raised when the hive is closed
        libcontext.socket(("evin", ("input", "mouse")), socket_flag())