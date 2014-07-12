import sys, libcontext
from libcontext.socketclasses import *

python2 = (sys.version_info[0] == 2)
python3 = (sys.version_info[0] == 3)

from .worker import worker
from .segments import *


class WorkerError(SystemError):

    def __init__(self, error):
        if isinstance(error, WorkerError):
            self.error = error.error

        else:
            self.error = error

    def __str__(self):
        return "\n Context: {}\n {}: {}".format(self.error[0], self.error[1][0].__name__, self.error[1][1])

    def __repr__(self):
        return self.__str__()


class raiser(worker):
    raisin = antenna("push", "exception")
    v_inp = variable("exception")
    connect(raisin, v_inp)

    @modifier
    def raising(self):
        if not self.raiser_active():
            return

        tb = sys.exc_info()[2]
        self.v_inp.cleared = True
        if self.v_inp[1][0] == WorkerError:
            if python2:
                exec("raise WorkerError, self.v_inp[1][1], tb")

            else:
                e2 = WorkerError(self.v_inp[1][1])
                e2.__traceback__ = tb
                raise e2
        else:
            if python2:
                exec("raise WorkerError, WorkerError(self.v_inp), tb")

            else:
                e2 = WorkerError(self.v_inp)
                e2.__traceback__ = tb
                raise e2

    trigger(v_inp, raising)

    def set_raiser_active(self, raiser_active):
        self.raiser_active = raiser_active

    def place(self):
        s = socket_single_required(self.set_raiser_active)
        libcontext.socket(("eventhandler", "raiser", "active"), s)
