import libcontext
from .segments import *
from . import worker, drone
from .bindworker import bindworker
from . import connect as hiveconnect
import inspect

from .types import _types as types
from .raiser import raiser

from .bind import *
from .bindbridge import bindbridge
from . import myobject, mytype


def get_reg_bindhelper(fr, dicvalues):
    from .hivemodule import allreg

    for value in dicvalues:
        try:
            allreg.add(value)

        except TypeError:  # cannot weakref everything
            pass

    ret = []
    if fr in reg_bindhelper.reg:
        for a in reg_bindhelper.reg[fr]:
            if a in allreg:
                continue

            allreg.add(a)
            ret.append(a)

        del reg_bindhelper.reg[fr]

    return ret


class staticbindbuilder(bindbuilder):

    def __new__(cls, name, bases, cls_dict):
        if name == "staticbind_baseclass":
            return mytype.__new__(cls, name, bases, cls_dict)

        inherited_class_dict = {}

        bindhelpers_nameless = []
        for base_cls_ in bases:
            if hasattr(base_cls_, "__bindhelpers__"):
                for h in base_cls_.__bindhelpers__:
                    if h not in bindhelpers_nameless:
                        bindhelpers_nameless.append(h)

        for base_cls_ in reversed(bases):
            cls_dict_ = base_cls_.__dict__

            if issubclass(base_cls_, bind_baseclass):
                cls_dict_ = dict(cls_dict_)
                cls_dict_.pop("bindname", None)

            inherited_class_dict.update(cls_dict_)

        old_bind_parameters = {}
        for key in inherited_class_dict:
            if isinstance(inherited_class_dict[key], bindparameter):
                old_bind_parameters[key] = inherited_class_dict[key]

        inherited_class_dict.update(cls_dict)

        caller_frame = id(inspect.currentframe().f_back)
        bindhelpers_nameless += get_reg_bindhelper(caller_frame, inherited_class_dict.values())
        inherited_class_dict["__bindhelpers__"] = bindhelpers_nameless
        bind_helpers = []

        for key in sorted(inherited_class_dict.keys()):
            attribute = inherited_class_dict[key]
            if isinstance(attribute, bindhelper):
                bind_helpers.append((key, attribute))

        bind_parameters = [h for h in bind_helpers if isinstance(h[1], bindparameter)]

        sorted_cls_dict = [(key, cls_dict[key]) for key in sorted(cls_dict.keys())]
        inherited_bind_parameters = [(item[0], bindparameter(item[1])) for item in sorted_cls_dict if
                                     item not in bind_parameters and item[0] in old_bind_parameters]

        bind_parameters += inherited_bind_parameters
        bind_parameter_names = set([h[0] for h in bind_parameters])

        bind_helpers.sort(key=lambda n: n[0])

        # Check for bindantennas
        for helper_name, helper in bind_helpers:
            if isinstance(helper, bindantenna) and helper_name != "bindname":
                raise TypeError("Static bind workers cannot take bindantennas")

        bind_helpers += [((index + 1), attribute) for index, attribute in enumerate(bindhelpers_nameless)]

        binders = [n[1] for n in bind_helpers if isinstance(n[1], binder)]
        for base_cls_ in binders:
            assert base_cls_.parametername in bind_parameter_names, base_cls_.parametername

        # Check for prebinders
        for helper_name, helper in bind_helpers:
            if isinstance(helper, prebinder):
                raise Exception("Prebinders not implemented for static bind bees")

        def get_bindhiveworker(*args, **kwargs):

            class bindhiveworker(bindworker):
                __beename__ = name + "-worker"

                bindworkerhive = inherited_class_dict["hive"]
                bindname = antenna("pull", "id")
                b_bindname = buffer("pull", "id")
                trigger_bindname = triggerfunc(b_bindname)
                connect(bindname, b_bindname)

                parameter = None
                for parameter in bind_parameters:
                    locals()[parameter[0]] = parameter[1].value  #changes can only be made by subclassing

                del parameter

                def do_bind(self):

                    class newhive(self.hive):
                        zzz_bindbridgedrone = bindbridge(self)
                        raiser = raiser()
                        hiveconnect("evexc", raiser)

                    hive = newhive().getinstance()
                    try:
                        libcontext.push(self._context.contextname)
                        hive.build(self.b_bindname)
                        hive.place()

                    finally:
                        libcontext.pop()

                    hive.close()
                    hive.init()

                    for startup_function in self.startupfunctions:
                        startup_function()

                    self.hives[self.b_bindname] = hive

                pause = antenna("push", "trigger")
                resume = antenna("push", "trigger")
                v_running = variable("bool")
                startvalue(v_running, True)

                @modifier
                def m_pause(self):
                    self.v_running = False

                trigger(pause, m_pause)

                @modifier
                def m_resume(self):
                    self.v_running = True

                trigger(resume, m_resume)

                stop = antenna("push", "id")
                v_stop = variable("id")
                connect(stop, v_stop)

                @modifier
                def m_stop(self):
                    del self.hives[self.v_stop]

                trigger(v_stop, m_stop)

                event = antenna("push", "event")
                v_event = variable("event")
                connect(event, v_event)

                @modifier
                def m_event(self):
                    event = self.v_event
                    if self.v_running:
                        for event_handler in self.eventfuncs:
                            event_handler(self, event)

                trigger(v_event, m_event)

                def init(self):
                    self.trigger_bindname()
                    self.do_bind()

                def place(self):
                    self.hives = {}
                    self.eventfuncs = []
                    self.binderinstances = []
                    self.startupfunctions = []

                    handled_parameters = set()

                    for binder in binders:
                        inst = binder.getinstance()
                        if inst is None:
                            continue

                        params = inst.parametername, inst.parametervalue, str(
                            inst.binderdroneinstance.__beename__), tuple(inst.antennanames)
                        if params in handled_parameters:
                            continue

                        handled_parameters.add(params)
                        self.binderinstances.append(inst)

                    for binder in self.binderinstances:
                        if getattr(self, binder.parametername) != binder.parametervalue:
                            continue

                        binder.place()

                    init_plugin = libcontext.pluginclasses.plugin_single_required(self.init)
                    libcontext.plugin("startupfunction", init_plugin)

            return bindhiveworker(*args, **kwargs)

        inherited_class_dict["worker"] = staticmethod(lambda *args, **kwargs: get_bindhiveworker(*args, **kwargs))
        return type.__new__(cls, name, (staticbind_baseclass,), inherited_class_dict)


from .segments._helpersegment import reg_helpersegment

import sys

python3 = (sys.version_info[0] == 3)
if python3:
    from .bind import bind_baseclass

    class staticbind_baseclass(bind_baseclass, myobject):
        __metaclass__ = staticbindbuilder
        hive = None  # make some prebinders that change self.hive if you need dynamic binding
        worker = None

else:
    class staticbind_baseclass(myobject):
        __metaclass__ = staticbindbuilder
        hive = None  # make some prebinders that change self.hive if you need dynamic binding
        worker = None

