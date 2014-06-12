import bee
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *


class mytext(object):
    metaguiparams = {"vartype": "type"}

    def __new__(cls, vartype):
        class mytext(bee.worker):
            string = output('pull', vartype)

            v_string = variable(vartype)
            parameter(v_string)

            connect(v_string, string)

        return mytext
      