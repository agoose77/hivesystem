import libcontext
from . import segments


def get_connector(mode, type):
    from .worker import worker

    class connector(worker):
        inp = segments.antenna(mode, type)
        outp = segments.output(mode, type)
        segments.connect(inp, outp)

    return connector()


class _io(object):
    inout = None

    def __init__(self, target, nosub=False, mode=None, type_=None):
        from .connect import connect

        assert isinstance(target, tuple) and len(target) == 2, target
        if isinstance(target[0], str):
            assert mode is not None
            assert type_ is not None
            tmode, ttype = mode, type_
            self.ttype = ttype
            self.tmode = tmode
        else:
            try:
                tmode, ttype = target[0]._wrapped_hive.guiparams[self.inout][target[1]]
                self.ttype = ttype
                self.tmode = tmode
            except KeyError:
                raise TypeError("%s has no %s '%s'" % (target[0], self.inout[:-1], target[1]))
            self.guiparams = target[0]._wrapped_hive.guiparams
        self.connector = get_connector(tmode, ttype).getinstance()
        target2 = target
        if isinstance(target[1], tuple):
            target2 = (target[0],) + target[1]
        if self.inout == "antennas":
            self.connection = connect(self.connector.outp, target2, nosub).getinstance()
        elif self.inout == "outputs":
            self.connection = connect(target2, self.connector.inp, nosub).getinstance()

    def build(self, hivename):
        self.hivename = hivename
        self.connector.build(hivename)

    def place0(self):
        self.connector.place()
        self.connector.parent = self
        for k in self.connector.context.plugins.keys():
            if k[1] == self.inout[:-1]:
                p = ("bee", k[1], self.hivename, self.ttype)
                libcontext.plugin(p, self.connector.context.plugins[k][0])
        for k in self.connector.context.sockets.keys():
            if k[1] == self.inout[:-1]:
                s = ("bee", k[1], self.hivename, self.ttype)
                libcontext.socket(s, self.connector.context.sockets[k][0])

    def place(self):
        self.connection.place()
        self.connect_contexts = self.connection.connect_contexts


class antenna_io(_io):
    inout = "antennas"


class output_io(_io):
    inout = "outputs"


from .hivemodule import beehelper


class antenna(beehelper):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        if len(self.args):
            self.target = self.args[0]
        elif "target" in self.kwargs:
            self.target = self.kwargs["target"]
        else:
            raise TypeError("bee.antenna must have a target")

    def getinstance(self, __parent__=None):
        self.instance = antenna_io(*self.args, **self.kwargs)
        return self.instance

    def set_parameters(self, name, parameters):
        pass

    def __getattr__(self, attr):
        if attr == "guiparams" and not isinstance(self.target[0], str):
            return self.target[0]._wrapped_hive.guiparams[self.inout][self.target[1]]
        try:
            ret = getattr(antenna_io, attr)
        except AttributeError:
            ret = (self, attr)
        return ret


class output(beehelper):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.instance = None
        if len(self.args):
            self.target = self.args[0]
        elif "target" in self.kwargs:
            self.target = self.kwargs["target"]
        else:
            raise TypeError("bee.output must have a target")

    def getinstance(self, __parent__=None):
        self.instance = output_io(*self.args, **self.kwargs)
        return self.instance

    def set_parameters(self, name, parameters):
        pass

    def __getattr__(self, attr):
        if attr == "guiparams" and not isinstance(self.target[0], str):
            return self.target[0]._wrapped_hive.guiparams[self.inout][self.target[1]]
        try:
            ret = getattr(output_io, attr)
        except AttributeError:
            ret = (self, attr)
        return ret
  
