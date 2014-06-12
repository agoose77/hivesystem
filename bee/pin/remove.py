import sys

python2 = (sys.version_info[0] == 2)
python3 = (sys.version_info[0] == 3)

import libcontext, libcontext.socketclasses
from ..drone import drone


def inspect_inputpin_push(pin):
    from ..segments._runtime_segment import _runtime_antenna_push

    for seg in pin._runtime_segments:
        if isinstance(seg, _runtime_antenna_push):
            s = seg.antenna_push_plugin.sockets[0]
            segments2 = s.function.im_self.beeinstance._runtime_segments
            for seg2 in segments2:
                if isinstance(seg2, _runtime_antenna_push):
                    c = seg2.antenna_push_plugin.counter
                    return c == 0


def inspect_inputpin_pull(pin):
    from ..segments._runtime_segment import _runtime_antenna_pull

    for seg in pin._runtime_segments:
        if isinstance(seg, _runtime_antenna_pull):
            if python2:
                segments2 = seg.inputfunc.im_self.beeinstance._runtime_segments
            elif python3:
                segments2 = seg.inputfunc.__self__.beeinstance._runtime_segments
            for seg2 in segments2:
                if isinstance(seg2, _runtime_antenna_pull):
                    c = seg2.inputfunc
                    return c is None


def inspect_outputpin_push(pin):
    from ..segments._runtime_segment import _runtime_output_push

    for seg in pin._runtime_segments:
        if isinstance(seg, _runtime_output_push):
            segments2 = seg.outputs[0].im_self.beeinstance._runtime_segments
            for seg2 in segments2:
                if isinstance(seg2, _runtime_output_push):
                    c = len(seg2.outputs)
                    return c == 0


def inspect_outputpin_pull(pin):
    from ..segments._runtime_segment import _runtime_output_pull

    for seg in pin._runtime_segments:
        if isinstance(seg, _runtime_output_pull):
            s = seg.output_pull_plugin.sockets[0]
            for seg2 in segments2:
                if isinstance(seg2, _runtime_output_pull):
                    c = seg2.output_pull_plugin.counter
                    return c == 0


class remove(drone):
    def __call__(self, pinworker):
        if pinworker not in self.mediator.pinworkerlist:
            raise ValueError("Cannot remove pinworker: unknown pinworker")
        pins = []
        for pintype, pin in self.mediator.pinworkers[pinworker]:
            ok = True
            if pintype == "push_input":
                ok = inspect_inputpin_push(pin)
                pins.append(pin)
            elif pintype == "pull_input":
                ok = inspect_inputpin_pull(pin)
                pins.append(pin)
            elif pintype == "push_output":
                ok = inspect_outputpin_push(pin)
                pins.append(pin)
            elif pintype == "pull_output":
                ok = inspect_outputpin_pull(pin)
                pins.append(pin)
            if not ok:
                s = "%s '%s'" % (pin.__beename__, pin._beename)
                raise TypeError("Cannot remove pinworker: %s is connected statically" % s)
        for source, target in list(self.pinconnect.connections):
            for pin in pins:
                if source is pin or target is pin:
                    self.disconnect(source, target)
        del self.mediator.pinworkers[pinworker]
        self.mediator.pinworkerlist.remove(pinworker)

    def set_mediator(self, mediator):
        self.mediator = mediator

    def set_disconnect(self, disconnect):
        self.disconnect = disconnect

    def set_pinconnect(self, pinconnect):
        self.pinconnect = pinconnect

    def place(self):
        s = libcontext.socketclasses.socket_single_required(self.set_disconnect)
        libcontext.socket(("pin", "disconnect"), s)
        s = libcontext.socketclasses.socket_single_required(self.set_pinconnect)
        libcontext.socket(("pin", "connect"), s)
        s = libcontext.socketclasses.socket_single_required(self.set_mediator)
        libcontext.socket(("pin", "mediator"), s)
