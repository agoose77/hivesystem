from ..segments import *
from ..worker import worker
import libcontext


class outputpin(object):
    metaguiparams = {"mode": "str", "type": "type"}

    def __new__(cls, mode, type, refresh=True):
        assert mode in ("push", "pull"), mode

        if mode == "push" and type == "trigger":
            class outputpin(worker):
                __pinmode__ = mode
                __pintype__ = type
                __pinclass__ = cls
                outp = output("push", "trigger")
                _push = triggerfunc(outp)
                value = variable("bool")
                parameter(value, None)

                def push(self):
                    v = self.value
                    if not v: return
                    self._push()
                    for o in self._outputs:
                        o()

                def _add_output(self, outputfunc):
                    self._outputs.append(outputfunc)

                def _remove_output(self, outputfunc):
                    try:
                        self._outputs.remove(outputfunc)
                    except ValueError:
                        raise PullInputError("Outputpin %s: cannot remove Output, Output unknown" % self.beename)

                def _refresh(self):
                    if self.refresh: self.value = None

                def place(self):
                    self._outputs = []
                    self.refresh = refresh
                    p = libcontext.pluginclasses.plugin_single_required(self, self.parent)
                    libcontext.plugin(("pin", "push_output"), p)

        elif mode == "push":
            class outputpin(worker):
                __pinmode__ = mode
                __pintype__ = type
                __pinclass__ = cls
                outp = output(mode, type)
                value = buffer(mode, type)
                parameter(value, None)
                connect(value, outp)
                _push = triggerfunc(value, "Output")

                def push(self):
                    v = self.value
                    if v is None: return
                    self._push()
                    for o in self._outputs:
                        o(v)

                def _add_output(self, outputfunc):
                    self._outputs.append(outputfunc)

                def _remove_output(self, outputfunc):
                    try:
                        self._outputs.remove(outputfunc)
                    except ValueError:
                        raise PullInputError("Outputpin %s: cannot remove Output, Output unknown" % self.beename)

                def _refresh(self):
                    if self.refresh: self.value = None

                def place(self):
                    self._outputs = []
                    self.refresh = refresh
                    p = libcontext.pluginclasses.plugin_single_required(self, self.parent)
                    libcontext.plugin(("pin", "push_output"), p)


        else:  # pull
            class outputpin(worker):
                __pinmode__ = mode
                __pintype__ = type
                __pinclass__ = cls
                outp = output(mode, type)
                value = buffer(mode, type)
                parameter(value, None)
                connect(value, outp)

                def _refresh(self):
                    if self.refresh: self.value = None

                def place(self):
                    self.refresh = refresh
                    p = libcontext.pluginclasses.plugin_single_required(self, self.parent)
                    libcontext.plugin(("pin", "pull_output"), p)
        outputpin.__metabee__ = cls
        return outputpin
  
