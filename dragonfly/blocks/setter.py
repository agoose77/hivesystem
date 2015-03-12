import bee
from bee.segments import *
import spyder, Spyder

from bee.event import exception
from bee.segments._runtime_segment import tryfunc

import libcontext
from libcontext.pluginclasses import *
from libcontext.socketclasses import *
import functools


def declare_subtree(catch, spydertypetree, setter, attriblist):
    for mname, mtypetree in spydertypetree.members:
        mtypename = mtypetree.typename
        if hasattr(mtypetree, "arraycount"):
            for c in range(mtypetree.arraycount): mtypename += "Array"
        mtype = getattr(Spyder, mtypename)

        catchf = functools.partial(catch, mname)
        i = ("bee", "Antenna", mname, mtypename)
        p = functools.partial(setter, attriblist + [mname])
        pp = tryfunc(catchf, p)
        libcontext.plugin(i, plugin_supplier(pp))

        if hasattr(mtypetree, "arraycount") and mtypetree.arraycount: continue
        nested = (hasattr(mtypetree, "members") and mtypetree.members is not None)
        if nested:
            c = libcontext.context(mname)
            libcontext.push(mname)
            declare_subtree(catch, mtypetree, setter, attriblist + [mname])
            libcontext.pop()


class setter(object):
    metaguiparams = {"spydertype": "type"}

    def __new__(cls, spydertype):
        assert spyder.validvar2(spydertype), spydertype
        spyderclass = getattr(Spyder, spydertype)
        spydertypetree = None
        try:
            spydertypetree = spyderclass._typetree()
            assert isinstance(spydertypetree, spyder.core.typetreeclass)
        except AttributeError:
            pass

        class setter(bee.worker):
            __nested_tuple__ = True
            _set = antenna("push", spydertype)
            on_set = output("push", "trigger")
            trig_on_set = triggerfunc(on_set)
            v_set = variable(spydertype)
            connect(_set, v_set)

            _copy = antenna("push", spydertype)
            v_copy = variable(spydertype)
            connect(_copy, v_copy)

            control = output_blockcontrol()

            @modifier
            def m_set(self):
                controls = self.control.get_blockcontrols()
                for control in controls:
                    control._set(self.v_set)
                self.trig_on_set()

            trigger(v_set, m_set)

            @modifier
            def m_copy(self):
                controls = self.control.get_blockcontrols()
                for control in controls:
                    control._set(c, copy=True)
                self.trig_on_set()

            trigger(v_copy, m_copy)

            def do_set(self, attributes, value):
                controls = self.control.get_blockcontrols()
                for control in controls:
                    c = control
                    for attrib in attributes:
                        c = getattr(c, attrib)
                    c._set(value)
                self.trig_on_set()

            def place(self):
                if spydertypetree is not None:
                    declare_subtree(self.catchfunc, spydertypetree, self.do_set, [])

        setter.guiparams["block"] = ("Antenna", "push", spydertype)
        return setter
