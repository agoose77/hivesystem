import functools
import libcontext
import sys

from . import PullInputError

import sys

python2 = (sys.version_info[0] == 2)
python3 = (sys.version_info[0] == 3)


def get_ident(identifier):
    if isinstance(identifier, str): return identifier
    if isinstance(identifier, int): return "%04d" % identifier
    raise Exception


catchfuncstack = []


def trywrapper(catchfunc, func, *args, **kwargs):
    global catchfuncstack
    from ..raiser import WorkerError

    try:
        ret = func(*args, **kwargs)
        return ret
    except Exception:
        if catchfunc in catchfuncstack:
            catchfuncstack = []
            raise
        old_catchfuncstack = list(catchfuncstack)
        try:
            exctype, value, tb = sys.exc_info()
            catchfuncstack.append(catchfunc)
            e = catchfunc(exctype, value)
            if not e.cleared: raise
        except WorkerError as e:
            if exctype == WorkerError:
                if python2:
                    exec("raise WorkerError, value, tb")
                else:
                    e2 = WorkerError(value)
                    e2.__traceback__ = tb
                    try:
                        raise e2
                    except Exception as e2:
                        e2.__context__ = None
                        raise
            else:
                e.__traceback__ = tb
                e.__context__ = None
                raise
        finally:
            catchfuncstack[:] = old_catchfuncstack[:]


def tryfunc(catchfunc, func):
    return functools.partial(trywrapper, catchfunc, func)


class _runtime_segment(object):
    connection_input = []
    connection_output = []
    _triggering_input = []
    _triggering_output = []
    _triggering_update = []
    _triggered_input = []
    _triggered_output = []
    _triggered_update = []
    segmentname = None
    type = None
    catchfunc = None
    pull_input_socketclass = libcontext.socketclasses.socket_single_required

    def __init__(self, inputmode, outputmode, beeinstance, beename):
        if inputmode not in ("push", "pull"):
            raise ValueError("Unknown input mode %s" % inputmode)
        if outputmode not in ("push", "pull"):
            raise ValueError("Unknown Output mode %s" % outputmode)
        self.inputmode = inputmode
        self.outputmode = outputmode
        self.beename = beename
        self.beeinstance = beeinstance

        self.pull_input = None
        self.push_outputs = []

        self.triggering_input = []
        self.triggering_output = []
        self.triggering_update = []
        self.triggering_input_pre = []
        self.triggering_output_pre = []
        self.triggering_update_pre = []
        self.triggered_input = []
        self.triggered_output = []
        self.triggered_update = []

    def set_catchfunc(self, catchfunc):
        self.input = tryfunc(catchfunc, self.input)
        self.output = tryfunc(catchfunc, self.output)
        self.update = tryfunc(catchfunc, self.update)

    def input(self, value):
        raise Exception("_runtime_segment input function must be overridden")

    def _trigger_pull_input00(self):
        self.input(self.pull_input())

    def _trigger_pull_input10(self):
        for target in self.triggering_input_pre:
            target()
        self.input(self.pull_input())

    def _trigger_pull_input01(self):
        self.input(self.pull_input())
        for target in self.triggering_input:
            target()

    def _trigger_pull_input11(self):
        for target in self.triggering_input_pre:
            target()
        self.input(self.pull_input())
        for target in self.triggering_input:
            target()

    def _trigger_push_input00(self, value):
        self.input(value)

    def _trigger_push_input10(self, value):
        for target in self.triggering_input_pre:
            target()
        self.input(value)

    def _trigger_push_input01(self, value):
        self.input(value)
        for target in self.triggering_input:
            target()

    def _trigger_push_input11(self, value):
        for target in self.triggering_input_pre:
            target()
        self.input(value)
        for target in self.triggering_input:
            target()

    def update(self):
        raise Exception("_runtime_segment update function must be overridden")

    def _trigger_update00(self):
        self.update()

    def _trigger_update10(self):
        for target in self.triggering_update_pre:
            target()
        self.update()

    def _trigger_update01(self):
        self.update()
        for target in self.triggering_update:
            target()

    def _trigger_update11(self):
        for target in self.triggering_update_pre:
            target()
        self.update()
        for target in self.triggering_update:
            target()


    def output(self):
        raise Exception("_runtime_segment Output function must be overridden")

    def _trigger_push_output00(self):
        value = self.output()
        if value is None: return
        for target in self.push_outputs: target(value)

    def _trigger_push_output10(self):
        for target in self.triggering_output_pre:
            target()
        value = self.output()
        if value is None: return
        for target in self.push_outputs: target(value)

    def _trigger_push_output01(self):
        value = self.output()
        if value is None: return
        for target in self.push_outputs: target(value)
        for target in self.triggering_output:
            target()

    def _trigger_push_output11(self):
        for target in self.triggering_output_pre:
            target()
        value = self.output()
        if value is None: return
        for target in self.push_outputs: target(value)
        for target in self.triggering_output:
            target()

    def _trigger_pull_output00(self):
        return self.output()

    def _trigger_pull_output10(self):
        for target in self.triggering_output_pre:
            target()
        return self.output()

    def _trigger_pull_output01(self):
        value = self.output()
        for target in self.triggering_output:
            target()
        return value

    def _trigger_pull_output11(self):
        for target in self.triggering_output_pre:
            target()
        value = self.output()
        for target in self.triggering_output:
            target()
        return value


    def set_pull_input(self, func):
        self.pull_input = func

    def add_push_output(self, func):
        self.push_outputs.append(func)


    def add_triggering(self, mode, func):
        t = getattr(self, "triggering_" + mode)
        assert hasattr(func, "__call__")
        t.append(func)

    def place(self):

        triggerings = set()

        pluginclass = libcontext.pluginclasses.plugin_single_required
        socketclass = libcontext.socketclasses.socket_single_required
        for mode in "input", "Output", "update":
            modes = {True: mode + "_pre", False: mode}
            for trigger, pre in getattr(self, "_triggering_" + mode):
                triggerings.add((mode, pre))
                func = functools.partial(self.add_triggering, modes[pre])
                libcontext.socket(("bee", "segment", "connection", get_ident(trigger.identifier)), socketclass(func))

        for mode in "input", "Output", "update":
            attr = "_trigger"
            if mode == "input": attr += "_" + self.inputmode
            if mode == "Output": attr += "_" + self.outputmode
            attr += "_" + mode
            funcs = {
                (False, False): getattr(self, attr + "00"),
                (True, False): getattr(self, attr + "10"),
                (False, True): getattr(self, attr + "01"),
                (True, True): getattr(self, attr + "11"),
            }
            b1 = (mode, True) in triggerings
            b2 = (mode, False) in triggerings
            func = funcs[b1, b2]
            setattr(self, "trigger_" + mode, func)

        if self.inputmode == "push":
            func = self.trigger_input
            for connection in self.connection_input:
                libcontext.plugin(("bee", "segment", "connection", get_ident(connection.identifier)), pluginclass(func))
        elif self.inputmode == "pull":
            func = self.set_pull_input
            if self.pull_input_socketclass == libcontext.socketclasses.socket_single_required:
                if len(self.connection_input) == 0:
                    raise PullInputError(
                        "Segment '%s' has pull input and must have exactly one input" % (self.segmentname))
            if len(self.connection_input) > 0:
                libcontext.socket(("bee", "segment", "connection", get_ident(self.connection_input[0].identifier)),
                                  libcontext.socketclasses.socket_single_required(func))
        else:
            raise ValueError()

        if self.outputmode == "push":
            func = self.add_push_output
            for connection in self.connection_output:
                libcontext.socket(("bee", "segment", "connection", get_ident(connection.identifier)), socketclass(func))
        elif self.outputmode == "pull":
            func = self.trigger_output
            for connection in self.connection_output:
                libcontext.plugin(("bee", "segment", "connection", get_ident(connection.identifier)), pluginclass(func))
        else:
            raise ValueError()

        for trigger in self._triggered_input:
            func = self.trigger_input
            libcontext.plugin(("bee", "segment", "connection", get_ident(trigger.identifier)), pluginclass(func))
        for trigger in self._triggered_output:
            func = self.trigger_output
            libcontext.plugin(("bee", "segment", "connection", get_ident(trigger.identifier)), pluginclass(func))
        for trigger in self._triggered_update:
            func = self.trigger_update
            libcontext.plugin(("bee", "segment", "connection", get_ident(trigger.identifier)), pluginclass(func))


class runtime_weaver(object):
    _inputs = []
    connection_output = []
    segmentname = None
    identifier = None

    def __init__(self, beeinstance, beename):
        self.beename = beename
        self.beeinstance = beeinstance
        self.inputs = [None, ] * len(self._inputs)

    def input(self):
        outp = tuple([f() for f in self.inputs])
        return outp

    def set_input(self, inputnr, inputfunc):
        self.inputs[inputnr] = inputfunc

    def set_catchfunc(self, catchfunc):
        self.input = tryfunc(catchfunc, self.input)

    def place(self):
        pluginclass = libcontext.pluginclasses.plugin_single_required
        socketclass = libcontext.socketclasses.socket_single_required
        for inr, connection in enumerate(self._inputs):
            func = functools.partial(self.set_input, inr)
            ident = self.identifier
            if ident is None: ident = str(id(self))
            identifier = ident + ":" + str(inr + 1)
            libcontext.socket(("bee", "segment", "connection", identifier), socketclass(func))
        for connection in self.connection_output:
            libcontext.plugin(("bee", "segment", "connection", get_ident(connection.identifier)),
                              pluginclass(self.input))


class runtime_unweaver(object):
    _outputs = []
    connection_input = []
    segmentname = None
    identifier = None

    def __init__(self, beeinstance, beename):
        self.beename = beename
        self.beeinstance = beeinstance
        self.outputs = [None, ] * len(self._outputs)

    def output(self, value):
        for v, outp in zip(value, self.outputs): outp(v)

    def set_catchfunc(self, catchfunc):
        self.output = tryfunc(catchfunc, self.output)

    def set_output(self, outputnr, outputfunc):
        self.outputs[outputnr] = outputfunc

    def place(self):
        pluginclass = libcontext.pluginclasses.plugin_single_required
        socketclass = libcontext.socketclasses.socket_single_required
        for onr, connection in enumerate(self._outputs):
            func = functools.partial(self.set_output, onr)
            ident = self.identifier
            if ident is None: ident = str(id(self))
            identifier = ident + ":" + str(onr + 1)
            libcontext.socket(("bee", "segment", "connection", identifier), socketclass(func))
        for connection in self.connection_input:
            libcontext.plugin(("bee", "segment", "connection", get_ident(connection.identifier)),
                              pluginclass(self.output))


class runtime_untoggler(object):
    _output1 = None
    _output2 = None
    connection_input = []
    segmentname = None
    identifier = None

    def __init__(self, beeinstance, beename):
        self.beename = beename
        self.beeinstance = beeinstance
        self.output1 = None
        self.output2 = None
        self.activated = False

    def set_catchfunc(self, catchfunc):
        self.output = tryfunc(catchfunc, self.output)

    def output(self):
        if not self.activated:
            self.activated = True
            self.output1()
        else:
            self.activated = False
            self.output2()

    def set_output1(self, outputfunc):
        self.output1 = outputfunc

    def set_output2(self, outputfunc):
        self.output2 = outputfunc

    def place(self):
        pluginclass = libcontext.pluginclasses.plugin_single_required
        socketclass = libcontext.socketclasses.socket_single_required
        ident = self.identifier
        if ident is None: ident = str(id(self))
        identifier = ident + ":1"
        libcontext.socket(("bee", "segment", "connection", identifier), socketclass(self.set_output1))
        identifier = ident + ":2"
        libcontext.socket(("bee", "segment", "connection", identifier), socketclass(self.set_output2))
        for connection in self.connection_input:
            libcontext.plugin(("bee", "segment", "connection", get_ident(connection.identifier)),
                              pluginclass(self.output))


class runtime_toggler(object):
    connection_output = []
    segmentname = None
    identifier = None

    def __init__(self, beeinstance, beename):
        self.beename = beename
        self.beeinstance = beeinstance
        self.outputs = []
        self.activated = False

    def set_catchfunc(self, catchfunc):
        self.output = tryfunc(catchfunc, self.output)

    def add_output(self, func):
        self.outputs.append(func)

    def get_input1(self):
        if not self.activated:
            self.activated = True
            self.output()

    def get_input2(self):
        if self.activated:
            self.activated = False
            self.output()

    def output(self):
        for f in self.outputs: f()

    def place(self):
        pluginclass = libcontext.pluginclasses.plugin_single_required
        socketclass = libcontext.socketclasses.socket_single_required
        ident = self.identifier
        if ident is None: ident = str(id(self))
        identifier = ident + ":1"
        libcontext.plugin(("bee", "segment", "connection", identifier), pluginclass(self.get_input1))
        identifier = ident + ":2"
        libcontext.plugin(("bee", "segment", "connection", identifier), pluginclass(self.get_input2))
        for connection in self.connection_output:
            libcontext.socket(("bee", "segment", "connection", get_ident(connection.identifier)),
                              socketclass(self.add_output))


class _runtime_test(object):
    connection_output = []
    segmentname = None
    identifier = None

    def __init__(self, beeinstance, beename):
        self.beename = beename
        self.beeinstance = beeinstance
        self.outputs = []
        self.activated = False

    def set_catchfunc(self, catchfunc):
        self.test = tryfunc(catchfunc, self.test)

    def add_output(self, func):
        self.outputs.append(func)

    def test(self, value):
        if value:
            for f in self.outputs: f()

    def place(self):
        pluginclass = libcontext.pluginclasses.plugin_single_required
        socketclass = libcontext.socketclasses.socket_single_required
        libcontext.plugin(("bee", "segment", "connection", self.identifier), pluginclass(self.test))
        for connection in self.connection_output:
            libcontext.socket(("bee", "segment", "connection", get_ident(connection.identifier)),
                              socketclass(self.add_output))


class _runtime_antenna_push(object):
    _connection = []
    segmentname = None
    type = None
    istrigger = None
    antenna_push_plugin = None

    def __init__(self, beeinstance, beename):
        self.beename = beename
        self.beeinstance = beeinstance
        self.connection = []
        if self.istrigger:
            self.input = self._input_trigger
        else:
            self.input = self._input

    def set_catchfunc(self, catchfunc):
        self.input = tryfunc(catchfunc, self.input)

    def add_connection(self, connection):
        self.connection.append(connection)

    def _input(self, value):
        for f in self.connection: f(value)

    def _input_trigger(self):
        for f in self.connection: f()

    def place(self):
        pluginclass = libcontext.pluginclasses.plugin_supplier
        self.antenna_push_plugin = pluginclass(self.input)
        libcontext.plugin(("bee", "Antenna", self.segmentname, self.type), self.antenna_push_plugin)
        socketclass = libcontext.socketclasses.socket_single_required
        for connection in self._connection:
            libcontext.socket(("bee", "segment", "connection", get_ident(connection.identifier)),
                              socketclass(self.add_connection))


class _runtime_antenna_pull(object):
    _connection = []
    segmentname = None
    type = None

    def __init__(self, beeinstance, beename):
        self.beename = beename
        self.beeinstance = beeinstance
        self.inputfunc = None

    def set_catchfunc(self, catchfunc):
        self.input = tryfunc(catchfunc, self.input)

    def set_input(self, inputfunc):
        self.inputfunc = inputfunc

    def input(self):
        if self.inputfunc is None: raise PullInputError(str(self.beename) + ":" + str(self.segmentname))
        return self.inputfunc()

    def place(self):
        socketclass = libcontext.socketclasses.socket_single_optional
        libcontext.socket(("bee", "Antenna", self.segmentname, self.type), socketclass(self.set_input))

        pluginclass = libcontext.pluginclasses.plugin_single_required
        for connection in self._connection:
            libcontext.plugin(("bee", "segment", "connection", get_ident(connection.identifier)),
                              pluginclass(self.input))


class _runtime_output_push(object):
    _connection = []
    segmentname = None
    type = None
    istrigger = None

    def __init__(self, beeinstance, beename):
        self.beename = beename
        self.beeinstance = beeinstance
        self.outputs = []
        if self.istrigger:
            self.output = self._output_trigger
        else:
            self.output = self._output

    def set_catchfunc(self, catchfunc):
        self.output = tryfunc(catchfunc, self.output)

    def add_output(self, output):
        self.outputs.append(output)

    def _output(self, value):
        for f in self.outputs: f(value)

    def _output_trigger(self):
        for f in self.outputs: f()

    def place(self):
        socketclass = libcontext.socketclasses.socket_supplier
        libcontext.socket(("bee", "Output", self.segmentname, self.type), socketclass(self.add_output))
        pluginclass = libcontext.pluginclasses.plugin_single_required
        for connection in self._connection:
            libcontext.plugin(("bee", "segment", "connection", get_ident(connection.identifier)),
                              pluginclass(self.output))


class _runtime_output_pull(object):
    _connection = []
    segmentname = None
    type = None
    output_pull_plugin = None

    def __init__(self, beeinstance, beename):
        self.beename = beename
        self.beeinstance = beeinstance
        self.input = None

    def set_catchfunc(self, catchfunc):
        self.output = tryfunc(catchfunc, self.output)

    def set_input(self, input):
        self.input = input

    def output(self):
        return self.input()

    def place(self):
        pluginclass = libcontext.pluginclasses.plugin_supplier
        self.output_pull_plugin = pluginclass(self.output)
        libcontext.plugin(("bee", "Output", self.segmentname, self.type), self.output_pull_plugin)

        socketclass = libcontext.socketclasses.socket_single_required
        connection = self._connection[0]
        libcontext.socket(("bee", "segment", "connection", get_ident(connection.identifier)),
                          socketclass(self.set_input))


class _runtime_operator(object):
    _connection_input = []
    _connection_output = []
    segmentname = None
    callback = (None,)
    intuple = None

    def __init__(self, beeinstance, beename):
        self.beename = beename
        self.beeinstance = beeinstance
        self.targets = []

    def set_catchfunc(self, catchfunc):
        self.runtuple = tryfunc(catchfunc, self.runtuple)
        self.runsingle = tryfunc(catchfunc, self.runsingle)

    def add_target(self, target):
        self.targets.append(target)

    def runtuple(self, cb, inp):
        value = cb(*inp)
        for f in self.targets: f(value)

    def runsingle(self, cb, inp):
        value = cb(inp)
        for f in self.targets: f(value)

    def place(self):
        pluginclass = libcontext.pluginclasses.plugin_single_required
        cb = getattr(self, "callback")[0]
        if self.intuple:
            r = self.runtuple
        else:
            r = self.runsingle
        p = pluginclass(functools.partial(r, cb))
        for connection in self._connection_input:
            libcontext.plugin(("bee", "segment", "connection", get_ident(connection.identifier)), p)
        socketclass = libcontext.socketclasses.socket_single_required
        for connection in self._connection_output:
            libcontext.socket(("bee", "segment", "connection", get_ident(connection.identifier)),
                              socketclass(self.add_target))


class _runtime_triggerfunc(object):
    segmentname = None  # must be overridden

    def __init__(self, beeinstance, beename):
        setattr(beeinstance, self.segmentname, self.call_targetfunc)

    def set_targetfunc(self, targetfunc):
        self.targetfunc = targetfunc

    def call_targetfunc(self):
        return self.targetfunc()

    def set_catchfunc(self, catchfunc):
        self.call_targetfunc = tryfunc(catchfunc, self.call_targetfunc)

    def place(self):
        socketclass = libcontext.socketclasses.socket_single_required
        libcontext.socket(("bee", "segment", "connection", self.segmentname), socketclass(self.set_targetfunc))


class _runtime_init(object):
    def __init__(self, beeinstance, beename):
        pass

    def set_targetfunc(self, targetfunc):
        self.targetfunc = targetfunc

    def trigger_target(self):
        self.targetfunc()

    def set_catchfunc(self, catchfunc):
        self.trigger_target = tryfunc(catchfunc, self.trigger_target)

    def place(self):
        socketclass = libcontext.socketclasses.socket_single_required
        libcontext.socket(("bee", "segment", "connection", self.segmentname), socketclass(self.set_targetfunc))
        pluginclass = libcontext.pluginclasses.plugin_single_required
        libcontext.plugin(("bee", "init"), pluginclass(self.trigger_target))


class _runtime_modifier(object):
    decorated = (None,)
    segmentname = None
    _triggered = []

    def __init__(self, beeinstance, beename):
        self.beeinstance = beeinstance
        self.decorated = self.decorated[0]

    def __call__(self):
        self.decorated(self.beeinstance)

    def set_catchfunc(self, catchfunc):
        self.decorated = tryfunc(catchfunc, self.decorated)

    def place(self):
        pluginclass = libcontext.pluginclasses.plugin_single_required
        for trigger in self._triggered:
            func = self
            libcontext.plugin(("bee", "segment", "connection", get_ident(trigger.identifier)), pluginclass(func))

