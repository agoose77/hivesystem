import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class mouse(bee.worker):
    """
    The mouse sensor reports any mouse input during the last tick
    """

    # What kind of mouse click events are we listening for?
    mode = variable("str")
    parameter(mode, "LClick")

    #Has a mouse event happened during the last tick?
    is_active = variable("bool")
    startvalue(is_active, False)
    active = output("pull", "bool")
    connect(is_active, active)

    #What are the X and Y positions? 
    vx = variable("int")
    startvalue(vx, 0)
    x = output("pull", "int")
    connect(vx, x)
    vy = variable("int")
    startvalue(vy, 0)
    y = output("pull", "int")
    connect(vy, y)

    # Mark "x" and "y" as an advanced output segment, and capitalize the I/O names
    guiparams = {
        "identifier": {"name": "Identifier", "fold": True},
        "x": {"name": "X Position", "advanced": True},
        "y": {"name": "Y Position", "advanced": True},
        "active": {"name": "Active"},
        "_memberorder": ["identifier", "x", "y", "active"],
    }

    # Method to manipulate the parameter form as it appears in the GUI
    @staticmethod
    def form(f):
        f.mode.name = "Detection mode"
        f.mode.type = "option"
        f.mode.options = "Move", "LClick", "RClick", "LDoubleClick", "MiddleClick", "LDrag", "RDrag"
        f.mode.optiontitles = "Move", "Left Click", "Right Click", "Double Click", "Middle Click", "Left Button Drag", "Right Button Drag"

    # Finally, declare our sockets and plugins, to communicate with the rest of the hive
    def place(self):
        raise NotImplementedError("sparta.sensors.mouse has not been implemented yet") 
        
      
      
