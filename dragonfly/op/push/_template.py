import bee
from bee.segments import *

class _template(object):
  def __new__(cls, op, inptypes, startvalues, outptypes, single_output=True):
    inps = ["inp"+str(n+1) for n in range(len(inptypes))]
    v_inps = ["v_inp"+str(n+1) for n in range(len(inptypes))]
    outps = ["outp"+str(n+1) for n in range(len(outptypes))]
    
    class worker(bee.worker):
      t = transistor(inptypes)      
      for inptype, v_inp, inp, start in zip(inptypes,v_inps,inps, startvalues):
        locals()[inp] = antenna("push", inptype)
        locals()[v_inp] = variable(inptype)
        startvalue(v_inp,start)
        connect(inp, v_inp) 
        trigger(v_inp, t, "update")
      for outptype, outp in zip(outptypes,outps):
        locals()[outp] = output("push", outptype)      
      w = weaver(inptypes, *v_inps)           
      connect(w, t)      
      if len(outptypes) == 1 and single_output == True:
        o = operator(op, inptypes, outptypes[0])
        connect(o, outps[0])
      else:
        o = operator(op, inptypes, outptypes)
        uw = unweaver(outptypes, *outps)
        connect(o, uw)
      connect(t, o)
    return worker
      
  
