import bee
from bee.segments import *
import libcontext
from libcontext.pluginclasses import *
from libcontext.socketclasses import *

import functools


class sequence(object):
    metaguiparams = {"number": "int"}

    def __new__(cls, number):
        number = int(number)
        assert number > 0, number

        class sequence(bee.worker):
            inp = antenna("pull", ("float", "fraction"))
            frac = variable(("float", "fraction"))
            trig = transistor(("float", "fraction"))
            connect(inp, trig)
            connect(trig, frac)

            def modfunc(self, n):
                v_outp = "v_outp" + str(n + 1)

                def frac():
                    f = self.frac
                    fmin = self.fracmin[n]
                    if f < fmin: return 0
                    fmax = self.fracmax[n]
                    if f >= fmax: return 1
                    return (f - fmin) / (fmax - fmin)

                setattr(self, v_outp, frac())

            for n in range(number):
                outp = "outp" + str(n + 1)
                locals()[outp] = output("pull", ("float", "fraction"))
                v_outp = "v_outp" + str(n + 1)
                locals()[v_outp] = variable(("float", "fraction"))
                connect(locals()[v_outp], locals()[outp])
                mod = "mod" + str(n + 1)
                locals()[mod] = modifier(functools.partial(modfunc, n=n))
                pretrigger(locals()[v_outp], trig)
                pretrigger(locals()[v_outp], mod)
                weight = "weight" + str(n + 1)
                locals()[weight] = variable(("float", "quantity"))
                parameter(weight)
            del outp, v_outp, mod, modfunc, weight

            def startup(self):
                weights = []
                for n in range(number):
                    weight = "weight" + str(n + 1)
                    w = getattr(self, weight)
                    if w <= 0: raise AssertionError("Weight %d must be greater than zero" % (n + 1))
                    weights.append(w)
                self.fracmin = []
                self.fracmax = []
                weightsum = sum(weights)
                cumweight = 0
                currmin = 0.0
                for w in weights:
                    self.fracmin.append(currmin)
                    cumweight += w
                    currmax = cumweight / weightsum
                    self.fracmax.append(currmax)
                    currmin = currmax

            def place(self):
                libcontext.plugin("startupfunction", plugin_single_required(self.startup))

        return sequence
