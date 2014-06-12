import traceback


class GetParameterException(Exception): pass


class get_parameter(object):
    def __init__(self, name, access_stack=[], callstack=None):
        self.name = name
        if not isinstance(name, str):
            raise TypeError("bee.get_parameter must be called with a string argument")
        self.name = name
        self.access_stack = access_stack
        self.callstack = callstack

    def get(self, parent, parameters):
        params = None
        if parent is not None:
            params = parent._hive_parameters
        if parameters is not None:
            params = parameters
        try:
            ret = params[self.name]
        except KeyError:
            if parent != None:
                raise KeyError("%s does not contain parameter '%s'" % (parent, self.name))
            else:
                raise KeyError("Parameters '%s' do not contain parameter '%s'" % (params.keys(), self.name))
        try:
            nn = ret
            for mode, attr, dmmy in self.access_stack:
                if mode == "getattr":
                    nn = getattr(nn, attr)
                elif mode == "getitem":
                    nn = nn[attr]
                elif mode == "call":
                    args, kwargs = attr, dmmy
                    nn = nn(*args, **kwargs)
                else:
                    raise Exception(mode)  # should never happen
            ret = nn
        except Exception as e:
            stack = self.callstack
            s1 = traceback.format_list(stack[:-1])
            tbstack = traceback.extract_tb(sys.exc_info()[2])
            s2 = traceback.format_list(tbstack[1:])
            s3 = traceback.format_exception_only(type(e), e)
            s = "\n" + "".join(s1 + s2 + s3)
            raise GetParameterException(s)

        return ret

    def getinstance(self, __parent__=None):
        return self

    def __getattr__(self, attr):
        if attr == "typename": raise AttributeError
        callstack = self.callstack
        if callstack is None: callstack = traceback.extract_stack()
        access_stack = list(self.access_stack)
        access_stack.append(("getattr", attr, None))
        return get_parameter(self.name, access_stack, callstack)

    def __getitem__(self, attr):
        callstack = self.callstack
        if callstack is None: callstack = traceback.extract_stack()
        access_stack = list(self.access_stack)
        access_stack.append(("getitem", attr, None))
        return get_parameter(self.name, access_stack, callstack)

    def __call__(self, *args, **kwargs):
        callstack = self.callstack
        if callstack is None: callstack = traceback.extract_stack()
        access_stack = list(self.access_stack)
        access_stack.append(("call", args, kwargs))
        return get_parameter(self.name, access_stack, callstack)

