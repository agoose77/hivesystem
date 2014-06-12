import libcontext, bee
from bee.segments import *
import spyder, Spyder
from ..models import statemachinestate
from libcontext.socketclasses import *
from libcontext.pluginclasses import *

class statemachine(bee.worker):
    """
    State machine actuator
    Every state has a name, and may have a process associated with it
    Whenever a state is activated, the associated process is launched or resumed
    """
    #Inputs and outputs
    trig = antenna("push", "trigger")    
    state = antenna("pull", "str")
    
    initial_state = variable("str")
    parameter(initial_state, "")
    
    states = variable("StateMachineStateArray")
    parameter(states, "")
    
    # Define the I/O names
    guiparams = {
      "trig" : {"name": "Trigger"},
      "state" : {"name": "State", "foldable": False},
      "_memberorder" : ["trig", "state"],
    }
            
    @classmethod
    def form(cls, f):
        f.states.name = "States"
        f.states.length = 10
        f.states.count_from_one = True
        f.states.form = "soft"
        f.states.arraymanager = "dynamic"
        f.states.default = Spyder.StateMachineStateArray()
        
        f.initial_state.name = "Initial state"
        
    def place(self):
        raise NotImplementedError("sparta.actuators.statemachine has not been implemented yet") 
    
    