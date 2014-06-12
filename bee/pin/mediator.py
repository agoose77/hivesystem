from .. import drone
from ..raiser import WorkerError
import libcontext
from libcontext.pluginclasses import *
from libcontext.socketclasses import *
from ..event import exception
import sys, functools

python2 = (sys.version_info[0] == 2)
python3 = (sys.version_info[0] == 3)


class mediator(drone):
    def __init__(self):
        self.pinworkerlist = []
        self.pinworkers = {}
        self._catch_targets = []

    def add_pin(self, pintype, pin, pinworker):
        if pinworker not in self.pinworkers:
            self.pinworkerlist.append(pinworker)
            self.pinworkers[pinworker] = []
        self.pinworkers[pinworker].append((pintype, pin))

    def add_pinworker(self, pinworker):
        self.add_pin("run", None, pinworker)

    def run(self):
        try:
            # for each pinworker:
            # - refresh pull outputs (clear their value)
            # - refresh pull inputs (get their value)
            # - run
            # - refresh push inputs (clear their value)
            # - push the push outputs
            for pinworker in list(self.pinworkerlist):
                if pinworker not in self.pinworkerlist: continue
                actions = self.pinworkers[pinworker]
                for pintype, pin in actions:
                    if pintype == "pull_output": pin._refresh()
                for pintype, pin in actions:
                    if pintype == "pull_input": pin._refresh()
                for pintype, pin in actions:
                    if pintype == "run" and pinworker.active:
                        pinworker.run()
                for pintype, pin in actions:
                    if pintype == "push_input": pin._refresh()
                for pintype, pin in actions:
                    if pintype == "push_output": pin.push()

            #refresh all push outputs (clear their value)
            for pinworker in self.pinworkerlist:
                actions = self.pinworkers[pinworker]
                for pintype, pin in actions:
                    if pintype == "push_output": pin._refresh()
        except Exception:
            try:
                exctype, value, tb = sys.exc_info()
                if pin is not None:
                    name = pinworker.context.contextname[-2:] + (pin._beename,)
                else:
                    name = pinworker.context.contextname[-2:]
                e = exception(name, (exctype, value))
                for c in self._catch_targets:
                    c(e)
                    if e.cleared: break
                if not e.cleared: raise
            except WorkerError as e:
                if exctype == WorkerError:
                    if python2:
                        exec("raise WorkerError, value, tb")
                    else:
                        e2 = WorkerError(value)
                        e2.__traceback__ = tb
                        raise e2
                else:
                    if python2:
                        exec("raise sys.exc_info()[0], sys.exc_info()[1], tb")
                    else:
                        e2 = sys.exc_info()[0](sys.exc_info()[1])
                        e2.__traceback__ = tb
                        raise e2

    def add_catch_target(self, catch_target):
        self._catch_targets.append(catch_target)

    def place(self):
        pintypes = ("push_input", "pull_input", "push_output", "pull_output")
        for pintype in pintypes:
            f = functools.partial(self.add_pin, pintype)
            libcontext.socket(("pin", pintype), socket_container(f))
        libcontext.socket(("pin", "run"), socket_container(self.add_pinworker))
        libcontext.plugin(("pin", "mediator"), plugin_supplier(self))

        p = plugin_single_required(("trigger", self.run, "tick", 0))
        libcontext.plugin(("evin", "listener"), p)

        libcontext.socket(("evexc", "exception"), socket_container(self.add_catch_target))
