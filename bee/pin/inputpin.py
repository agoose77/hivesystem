from ..segments import *
from ..worker import worker
import libcontext


class inputpin(object):
    metaguiparams = {"mode": "str", "type": "type"}

    def __new__(cls, mode, type, refresh=True):
        assert mode in ("push", "pull"), mode

        if mode == "pull":
            class inputpin(worker):
                __pinmode__ = mode
                __pintype__ = type
                __pinclass__ = cls
                inp = antenna(mode, type)
                value = buffer(mode, type)
                parameter(value, None)
                connect(inp, value)
                _get_static_input = triggerfunc(value, "input")

                def get_value(self):
                    has_static_input = True
                    try:
                        self._get_static_input()
                    except PullInputError:
                        has_static_input = False

                    if has_static_input is True:
                        if self._input is not None:
                            raise PullInputError("Inputpin %s can have only one input" % self._beename)
                        else:
                            return self.value
                    else:
                        if self._input is None:
                            raise PullInputError("Inputpin %s has no input" % self._beename)
                        else:
                            self.value = self._input()
                            return self.value

                def _set_input(self, inputfunc):
                    if self._input is not None:
                        raise PullInputError("Inputpin %s can have only one input" % self._beename)
                    self._input = inputfunc

                def _remove_input(self, inputfunc):
                    if inputfunc is None:
                        raise PullInputError("Inputpin %s: cannot remove input, input is None" % self._beename)
                    elif inputfunc != self._input:
                        raise PullInputError("Inputpin %s: cannot remove input, input unknown" % self._beename)
                    self._input = None

                def _refresh(self):
                    if self.refresh: self.get_value()

                def place(self):
                    self._input = None
                    self.refresh = refresh
                    p = libcontext.pluginclasses.plugin_single_required(self, self.parent)
                    libcontext.plugin(("pin", "pull_input"), p)
        elif mode == "push" and type == "trigger":
            class inputpin(worker):
                __pinmode__ = mode
                __pintype__ = type
                __pinclass__ = cls
                inp = antenna("push", "trigger")
                v_true = variable("bool")
                startvalue(v_true, True)
                value = buffer("push", "bool")
                parameter(value, None)
                t_value = transistor("bool")
                connect(v_true, t_value)
                connect(t_value, value)
                trigger(inp, t_value)

                def _refresh(self):
                    if self.refresh: self.value = None

                def place(self):
                    self.refresh = refresh
                    p = libcontext.pluginclasses.plugin_single_required(self, self.parent)
                    libcontext.plugin(("pin", "push_input"), p)

        else:  # push
            class inputpin(worker):
                __pinmode__ = mode
                __pintype__ = type
                __pinclass__ = cls
                inp = antenna(mode, type)
                value = buffer(mode, type)
                parameter(value, None)
                connect(inp, value)

                def _refresh(self):
                    if self.refresh: self.value = None

                def place(self):
                    self.refresh = refresh
                    p = libcontext.pluginclasses.plugin_single_required(self, self.parent)
                    libcontext.plugin(("pin", "push_input"), p)

        inputpin.__metabee__ = cls
        return inputpin
  
