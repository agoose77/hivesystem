import bee
from bee.segments import *
import spyder, Spyder

from bee.event import exception
from bee.segments._runtime_segment import tryfunc

import libcontext
from libcontext.pluginclasses import *
from libcontext.socketclasses import *
import functools


def declare_subtree(catch, spydertypetree, getter, attriblist):
    for mname, mtypetree in spydertypetree.members:
        mtypename = mtypetree.typename
        if hasattr(mtypetree, "arraycount"):
            for c in range(mtypetree.arraycount): mtypename += "Array"
        mtype = getattr(Spyder, mtypename)

        catchf = functools.partial(catch, mname)
        i = ("bee", "output", mname, mtypename)
        p = functools.partial(getter, attriblist + [mname])
        pp = tryfunc(catchf, p)
        libcontext.plugin(i, plugin_supplier(pp))

        if hasattr(mtypetree, "arraycount") and mtypetree.arraycount: continue
        nested = (hasattr(mtypetree, "members") and mtypetree.members is not None)
        if nested:
            c = libcontext.context(mname)
            libcontext.push(mname)
            declare_subtree(catch, mtypetree, getter, attriblist + [mname])
            libcontext.pop()


class getter(object):
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

        class getter(bee.worker):
            _self = output("pull", spydertype)
            v_self = variable(spydertype)
            connect(v_self, _self)

            model = antenna("pull", "blockmodel")
            v_model = buffer("pull", "blockmodel")
            connect(model, v_model)
            trig_model = triggerfunc(v_model)

            @modifier
            def m_get(self):
                self.v_self = self.v_model._get()

            pretrigger(v_self, v_model)
            pretrigger(v_self, m_get)

            def do_get(self, attributes):
                ret = self.v_model._get()
                for a in attributes:
                    ret = getattr(ret, a)
                return ret

            def place(self):
                p = plugin_single_required(self.trig_model)
                libcontext.plugin(("bee", "init"), p)
                if spydertypetree is not None:
                    declare_subtree(self.catchfunc, spydertypetree, self.do_get, [])

        getter.guiparams["block"] = ("output", "pull", spydertype)
        return getter
