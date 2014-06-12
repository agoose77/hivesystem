import bee
from bee.segments import *

import bee.segments.test

def isnotfunc(v):
  return not v

class test(bee.worker):
  inp = antenna("push","bool")
  outp_if = output("push", "trigger")
  outp_else = output("push", "trigger")

  subtest = bee.segments.test(inp)
  connect(subtest, outp_if)

  isnot = operator(isnotfunc,"bool","bool")
  connect(inp, isnot)
  subtest2 = bee.segments.test(isnot)
  connect(subtest2, outp_else)
