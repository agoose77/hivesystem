import libcontext, functools, traceback, sys
from .hivemodule import BeeHelper
from .resolve import resolve
from .beewrapper import BeeWrapper


class ConfigureBeeException(Exception):
    pass


class delayedcall(object):

    def __init__(self, parent, appendfunc, attrs, stack):
        self.parent = parent
        self.appendfunc = appendfunc
        self.attrs = attrs
        self.stack = stack

    def __call__(self, *args, **kargs):
        self.appendfunc(self.attrs, self.stack, *args, **kargs)
        return self.parent

    def __getattr__(self, attr):
        newattrs = list(self.attrs)
        newattrs.append(("getattr", attr))
        return delayedcall(self.parent, self.appendfunc, newattrs, self.stack)

    def __getitem__(self, attr):
        newattrs = list(self.attrs)
        newattrs.append(("getitem", attr))
        return delayedcall(self.parent, self.appendfunc, newattrs, self.stack)


class ConfigureBase(BeeHelper):

    __reg_enabled__ = False

    def getinstance(self, __parent__=None):
        return self

    def configure(self, beedict):
        pass

    def bind(self):
        pass

    def place(self):
        pass

    def hive_init(self, beedict):
        pass

    def set_parameters(self, name, params):
        pass


class Configure(ConfigureBase):

    def __init__(self, target):
        self.target_original = target
        self.configuration = []

        self.target = target
        self.bound_target = True

        if isinstance(target, str):
            self.target = target

        elif hasattr(target, "__get_beename__"):
            self.target = target
            self.bound_target = False

        else:
            raise TypeError(target)

    def bind(self):
        if not self.bound_target:
            if isinstance(self.target.__get_beename__, tuple):
                raise TypeError(self.target)

            self.target = self.target.__get_beename__(self.target)
            self.bound_target = True

    def configure(self, beedict):
        if not self.bound_target:
            from .drone import drone

            if isinstance(self.target.instance, drone) and self.target.instance in beedict.values():
                self.target = [v for v in beedict if beedict[v] is self.target.instance][0]

            else:
                self.bind()

        n = beedict[self.target]
        n = resolve(n, parameters=self.parameters)

        if n is self:
            raise Exception("bee.Configure target '%s' is self" % self.target)

        from .worker import workerframe

        if isinstance(n, BeeWrapper):
            assert n.instance is not None
            n = n.instance

        if isinstance(n, workerframe):
            assert n.built
            n = n.bee

        for attrs, stack, args, kargs in self.configuration:
            args = tuple([resolve(a, parameters=self.parameters) for a in args])
            kargs = dict((a, resolve(kargs[a], parameters=self.parameters)) for a in kargs)
            try:
                nn = n
                setitem = False
                for mode, attr in attrs:
                    if mode == "getattr":
                        nn = getattr(nn, attr)
                    elif mode == "getitem":
                        nn = nn[attr]
                    elif mode == "setitem":
                        attr, value = attr
                        nn[attr] = value
                        setitem = True
                    else:
                        raise Exception(mode)  # should never happen
                if not setitem:
                    nn(*args, **kargs)
            except Exception as e:
                s1 = traceback.format_list(stack[:-1])
                tbstack = traceback.extract_tb(sys.exc_info()[2])
                s2 = traceback.format_list(tbstack[1:])
                s3 = traceback.format_exception_only(type(e), e)
                s = "\n" + "".join(s1 + s2 + s3)
                raise ConfigureBeeException(s)

        if isinstance(n, ConfigureBase):
            n.configure()

    def set_parameters(self, name, parameters):
        self.parameters = parameters

    def __configure_append__(self, attr, stack, *args, **kargs):
        self.configuration.append((attr, stack, args, kargs))
        return self

    def __getattr__(self, attr):
        if attr == "typename":
            raise AttributeError

        stack = traceback.extract_stack()
        return delayedcall(self, self.__configure_append__, [("getattr", attr)], stack)

    def __getitem__(self, attr):
        stack = traceback.extract_stack()
        return delayedcall(self, self.__configure_append__, [("getitem", attr)], stack)

    def __setitem__(self, attr, value):
        stack = traceback.extract_stack()
        at = [("setitem", (attr, value))]
        self.configuration.append((at, stack, [], {}))


class ConfigureMultiple(ConfigureBase):

    def __init__(self, *targets):
        self.targets = []

        for target in targets:
            try:
                assert isinstance(target, ConfigureBase)

            except AssertionError:
                if not isinstance(target, list):
                    raise

                target = ConfigureMultiple(*target)

            self.targets.append(target)

    def bind(self):
        for t in self.targets:
            t.bind()

    def configure(self, beedict):
        for t in self.targets:
            t.configure(beedict)

    def set_parameters(self, name, params):
        for t in self.targets:
            t.set_parameters(name, params)

    def hive_init(self, beedict):
        for t in self.targets:
            t.hive_init(beedict)

