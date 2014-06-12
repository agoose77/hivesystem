import bee
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *
  
class mytext(bee.worker):
  string = output('pull', 'str')
  
  v_string = variable('str')
  parameter(v_string)
  
  connect(v_string, string)