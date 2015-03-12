from ..hivemodule import HiveBuilderMeta, appcontext
from .. import frame, hive
from ..drone import drone
from ..worker import workerbuilder
import libcontext


class _pinworkerbuilder(HiveBuilderMeta):
    def __new__(metacls, name, bases, dic, *args, **kargs):
        from .inputpin import inputpin
        from .outputpin import outputpin
        from .. import Antenna, Output

        for d in list(dic.keys()):
            b = dic[d]
            if hasattr(b, "__metabee__") and not isinstance(b.__metabee__, tuple):
                if isinstance(b, workerbuilder): b = b()
                m = b.__metabee__
                if m == inputpin:
                    a = Antenna(b.inp, nosub=True)
                    dic["@" + d] = a
                elif m == outputpin:
                    o = Output(b.outp, nosub=True)
                    dic["@" + d] = o
                dic[d] = b
        return HiveBuilderMeta.__new__(
            metacls, name, bases, dic, specialmethods=["run"], **kargs
        )


class pinworkerapp(drone):
    def __init__(self):
        self.active = True

    def place(self):
        p = libcontext.pluginclasses.plugin_single_required(self.parent)
        libcontext.import_socket(self.parent.parent.context, ("pin", "run"))
        libcontext.import_socket(self.parent.parent.context, ("pin", "push_input"))
        libcontext.import_socket(self.parent.parent.context, ("pin", "pull_input"))
        libcontext.import_socket(self.parent.parent.context, ("pin", "push_output"))
        libcontext.import_socket(self.parent.parent.context, ("pin", "pull_output"))

        libcontext.plugin(("pin", "run"), p)


class pinworker(hive):
    __metaclass__ = _pinworkerbuilder
    _hivecontext = appcontext(pinworkerapp)

    def run(self): pass


del pinworkerapp


