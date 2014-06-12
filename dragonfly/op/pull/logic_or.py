import bee
from bee.segments import *


class logic_or(bee.worker):
  inp1 = antenna("pull","bool")
  inp2 = antenna("pull","bool")
  w_inp = weaver(("bool","bool"), inp1, inp2)
  t_inp = transistor(("bool", "bool"))
  connect(w_inp, t_inp)

  o = operator(lambda inp1, inp2: inp1 or inp2, ("bool","bool"), "bool")
  connect(t_inp, o)
  
  outp = output("pull","bool")
  v_outp = variable("bool")
  connect(v_outp, outp)
  connect(o, v_outp)
  
  pretrigger(v_outp, t_inp)
