import libcontext, bee
from bee.segments import *
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class object_(bee.worker):
    """
    The object actuator creates a new 3D object of "object class" at "location".  
    If a process class of the same name as "object class" has been registered, launch it. 
    Output contains the name of the last spawned object.
    """

    # Inputs and outputs
    trig = antenna("push", "trigger")
    class_ = antenna("pull", ("str", "identifier"))
    placement = antenna("pull", ("object", "matrix"))

    output_entity = output("pull", ("str", "identifier"))
    v_output_entity = variable(("str", "identifier"))
    connect(v_output_entity, output_entity)

    output_process = output("pull", ("str", "identifier"))
    v_output_process = variable(("str", "identifier"))
    connect(v_output_process, output_process)

    subprocess = variable("bool")
    parameter(subprocess, True)

    # Mark "object class" as an initially folded, and define the I/O names
    guiparams = {
        "trig": {"name": "Trigger"},
        "class_": {"name": "Object Class", "fold": True},
        "placement": {"name": "Object Placement"},
        "output_entity": {"name": "Output"},
        "output_process": {"name": "Output"},
        "_memberorder": ["trig", "class_", "placement", "output_process", "output_entity"],
    }

    # Method to manipulate the parameter form as it appears in the GUI
    @staticmethod
    def form(f):
        f.subprocess.name = "Subprocess mode"
        f.subprocess.advanced = True

    # Finally, declare our sockets and plugins, to communicate with the rest of the hive
    def place(self):
        raise NotImplementedError("sparta.sensors.object_ has not been implemented yet") 
        
      
     