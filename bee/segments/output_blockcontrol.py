from ._io_base import io_base
import libcontext
from ._runtime_segment import tryfunc


class _runtime_output_blockcontrol(object):
    segmentname = None
    output_push_socket = None

    def __init__(self, beeinstance, beename):
        self.beename = beename
        self.beeinstance = beeinstance
        self.get_blockcontrols = self._get_blockcontrols
        self._blockcontrols = []
        setattr(beeinstance, self.segmentname, self)

    def _add_blockcontrol(self, blockcontrol):
        self._blockcontrols.append(blockcontrol)

    def _get_blockcontrols(self):
        return [f() for f in self._blockcontrols]

    def set_catchfunc(self, catchfunc):
        self.get_blockcontrols = tryfunc(catchfunc, self.get_blockcontrols)

    def place(self):
        socketclass = libcontext.socketclasses.socket_container
        self.output_push_socket = socketclass(self._add_blockcontrol)
        libcontext.socket(("bee", "Output", self.segmentname, "blockcontrol"), self.output_push_socket)


class output_blockcontrol(io_base):
    def __init__(self):
        pass

    def guiparams(self, segmentname, guiparams):
        pnam = "outputs"
        if pnam not in guiparams:
            guiparams[pnam] = {}
        p = ("push", "blockcontrol")
        guiparams[pnam][segmentname] = p

    def build(self, segmentname):
        self.segmentname = segmentname
        dic = {
            "segmentname": segmentname,
        }
        return type("runtime_output_blockcontrol:" + segmentname, (_runtime_output_blockcontrol,), dic)
