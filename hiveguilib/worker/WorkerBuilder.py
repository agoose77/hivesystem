from __future__ import print_function, absolute_import

"""
Builds worker templates and instantiates them with get_copy
Also builds worker templates from metaworker templates
"""

support_simplified = False  # if enabled, also build the "simplified" profile

from ..HGui import Attribute, Hook
from ..params import get_paramtypelist, get_param_pullantennas, parse_paramtypelist, typetuple
from .WorkerInstanceManager import WorkerInstance

from collections import namedtuple

import copy
import functools


WorkerData = namedtuple("WorkerData", ("beename", "antennas", "outputs", "ev", "paramnames", "paramtypelist", "block", "guiparams",
                         "tooltip"))

def keyfunc(memberorder, a):
    name = a[0]
    if name in memberorder:
        return memberorder.index(name)
    else:
        return name


def freeze(items):
    import Spyder

    items2 = []
    for n, v in items:
        if isinstance(v, Spyder.Object): v = v.dict()
        if isinstance(v, list): v = freeze(enumerate(v))
        if isinstance(v, dict): v = freeze(v.items())
        items2.append((n, v))
    return frozenset(items2)


class WorkerMapping(object):
    def __init__(self):
        self._inmap = {}  # Describes the mapping from antennas to attribute inhooks
        self._pmap = {}  # Describes the mapping from parameters to attribute values
        self._outmap = {}  # Describes the mapping from outputs to attribute outhooks
        self._inmapr = {}  # Describes the mapping from attribute inhooks to antennas
        self._pmapr = {}  # Describes the mapping from attribute values to parameters
        self._outmapr = {}  # Describes the mapping from attribute outhooks to outputs

    def set_inmap(self, m):
        self._inmap = m
        r = {}
        for k, v in m.items():
            if v != None: r[v] = k
        self._inmapr = r

    def get_inmap(self):
        return self._inmap

    inmap = property(get_inmap, set_inmap)

    def set_pmap(self, m):
        self._pmap = m
        r = {}
        for k, v in m.items():
            if v != None: r[v] = k
        self._pmapr = r

    def get_pmap(self):
        return self._pmap

    pmap = property(get_pmap, set_pmap)

    def set_outmap(self, m):
        self._outmap = m
        r = {}
        for k, v in m.items():
            if v != None: r[v] = k
        self._outmapr = r

    def get_outmap(self):
        return self._outmap

    outmap = property(get_outmap, set_outmap)


def build_droneinstance():
    global droneinstance
    args = ["arg1", "arg2", "arg3", "arg4", "arg5"]
    m = dict(zip(args, [None] * len(args)))
    mapping = WorkerMapping()
    mapping.set_pmap(m)
    droneinstance = WorkerInstance("drone", {"default": ([], mapping)}, args,
                                   [(("expression", str, 'no-defaultvalue'), None)] * 5,  None, {}, "DRONE TOOLTIP")


build_droneinstance()


def build_zeroinstance():
    global zeroinstance
    mapping = WorkerMapping()
    mapping.set_inmap({})
    mapping.set_outmap({})
    zeroinstance = WorkerInstance(
        "spydermap",
        {"default": ([], mapping)},
        [],
        [],
        None, {},
        "ZERO TOOLTIP"
    )


build_zeroinstance()


def build_worker_plain(beename, antennas, outputs, ev, paramnames, paramtypelist, guiparams):
    if paramnames is None: raise Exception(beename)
    mapping = WorkerMapping()
    attribs = []
    attrs = [(pname, "antenna", pval) for pname, pval in antennas.items()] + \
            [(pname, "output", pval) for pname, pval in outputs.items()]
    memberorder = guiparams.get("guiparams", {}).get("_memberorder", {})
    attrs.sort(key=functools.partial(keyfunc, memberorder))

    names = {}
    guiparams2 = {}
    if guiparams is not None:
        guiparams2 = guiparams.get("guiparams", {})
    for pname, io, pval in attrs:
        label = pname
        if pname in guiparams2:
            p = guiparams2[pname]
            if "name" in p: label = p["name"]
        names[pname] = label

    inmap, outmap, pmap = mapping.inmap, mapping.outmap, mapping.pmap
    for pname, io, pval in attrs:
        mode, type_ = pval
        h = Hook(mode, type_)
        if io == "antenna":
            inh, outh = h, None
            inmap[pname] = pname
        else:
            inh, outh = None, h
            outmap[pname] = pname
        a = Attribute(
            pname,
            inh, outh,
            label=names[pname]
        )
        attribs.append(a)
    for pname in "evin", "evout", "everr", "evexc":
        if pname not in ev: continue
        if pname == "evin":
            inmap[pname] = None
        else:
            outmap[pname] = None
    for paramname in paramnames:
        pmap[paramname] = None
    mapping.inmap, mapping.outmap, mapping.pmap = inmap, outmap, pmap
    return attribs, mapping


def build_worker_default(beename, antennas, outputs, ev, paramnames, paramtypelist, guiparams):
    if paramnames is None:
        raise Exception(beename)
    mapping = WorkerMapping()
    attribs = []
    attrs = [(pname, "antenna", pval) for pname, pval in antennas.items()] + \
            [(pname, "output", pval) for pname, pval in outputs.items()]
    memberorder = guiparams.get("guiparams", {}).get("_memberorder", {})
    attrs.sort(key=functools.partial(keyfunc, memberorder))

    names = {}
    guiparams2 = {}
    if guiparams is not None:
        guiparams2 = guiparams.get("guiparams", {})
    for pname, io, pval in attrs:
        label = pname
        if pname in guiparams2:
            p = guiparams2[pname]
            if "name" in p: label = p["name"]
        names[pname] = label

    inmap, outmap, pmap = mapping.inmap, mapping.outmap, mapping.pmap

    has_value = False
    valuetype = None
    if not ("value" in paramnames and "v" in paramnames):
        for vv in "value", "v":
            if vv in paramnames:
                has_value = True
                d = dict(zip(paramnames, paramtypelist))
                valuetype = d[vv][0][0]
                pmap[vv] = "value"

    for pname, io, pval in attrs:
        if io == "antenna" and pname == "inp":
            t = pval[1]
            if isinstance(t, tuple) and not typetuple(t): t = t[0]
            if t == "id": t = "str"
            if has_value == True and t != valuetype:
                has_value = False
            break
        if io == "output" and pname == "outp":
            t = pval[1]
            if isinstance(t, tuple) and not typetuple(t): t = t[0]
            if t == "id": t = "str"
            if has_value == True and t != valuetype:
                has_value = False
            break

    if has_value:
        a_value = Attribute("value", type=valuetype)
        attribs.append(a_value)
    for pname, io, pval in attrs:
        mode, type_ = pval
        h = Hook(mode, type_)
        if io == "antenna":
            if has_value and pname == "inp":
                a_value.inhook = h
                inmap[pname] = "value"
                continue
            inh, outh = h, None
            inmap[pname] = pname
        else:
            if has_value and pname == "outp":
                a_value.outhook = h
                outmap[pname] = "value"
                continue
            inh, outh = None, h
            outmap[pname] = pname
        a = Attribute(
            pname,
            inh, outh,
            label=names[pname],
        )
        attribs.append(a)
    for pname in "evin", "evout", "everr", "evexc":
        if pname not in ev: continue
        if pname == "evin":
            inmap[pname] = None
        else:
            outmap[pname] = None
    for paramname in paramnames:
        if paramname not in pmap:
            pmap[paramname] = None
    mapping.inmap, mapping.outmap, mapping.pmap = inmap, outmap, pmap
    return attribs, mapping


def attribs_append_evio(attribs, mapping, ev):
    inmap, outmap, pmap = mapping.inmap, mapping.outmap, mapping.pmap

    if "evin" in ev:
        h = Hook("push", "event")
        a = Attribute(
            "evin",
            h, None
        )
        inmap["evin"] = "evin"
        attribs.append(a)

    if "evout" in ev:
        h = Hook("push", "event")
        a = Attribute(
            "evout",
            None, h
        )
        outmap["evout"] = "evout"
        attribs.append(a)

    if "everr" in ev:
        h = Hook("push", "event")
        a = Attribute(
            "everr",
            None, h
        )
        outmap["everr"] = "everr"
        attribs.append(a)

    if "evexc" in ev:
        h = Hook("push", "exception")
        a = Attribute(
            "evexc",
            None, h
        )
        outmap["evexc"] = "evexc"
        attribs.append(a)
    mapping.inmap, mapping.outmap, mapping.pmap = inmap, outmap, pmap


def build_worker_plain_evio(*args, **kwargs):
    if "ev" in kwargs:
        ev = kwargs["ev"]
    else:
        ev = args[3]
    attribs, mapping = build_worker_plain(*args, **kwargs)
    attribs_append_evio(attribs, mapping, ev)
    return attribs, mapping


def build_worker_default_evio(*args, **kwargs):
    if "ev" in kwargs:
        ev = kwargs["ev"]
    else:
        ev = args[3]
    attribs, mapping = build_worker_default(*args, **kwargs)
    attribs_append_evio(attribs, mapping, ev)
    return attribs, mapping


def build_worker_simplified(beename, antennas, outputs, ev, paramnames, paramtypelist, guiparams):
    if guiparams is None or "guiparams" not in guiparams: return None, None
    advanced = []
    g = guiparams["guiparams"]
    for k in g:
        try:
            g[k].get
        except AttributeError:
            continue
        if g[k].get("advanced", False): advanced.append(k)
    if len(advanced) == 0: return None, None

    attribs, mapping = build_worker_default(beename, antennas, outputs, ev, paramnames, paramtypelist, guiparams)
    attribs = [a for a in attribs if a.name not in advanced]
    for a in advanced:
        if a in mapping.inmap: mapping.inmap[a] = None
        if a in mapping.outmap: mapping.outmap[a] = None
    return attribs, mapping


import spyder, Spyder


def block_subtree(spydertypetree, attribstack=[]):
    ret = {}
    for mname, mtypetree in spydertypetree.members:
        mtypename = mtypetree.typename
        if hasattr(mtypetree, "arraycount"):
            for c in range(mtypetree.arraycount): mtypename += "Array"

        header = ".".join(attribstack)
        if len(header): header += "."
        mfullname = header + mname
        ret[mfullname] = mtypename

        mtype = getattr(Spyder, mtypename)
        if hasattr(mtypetree, "arraycount") and mtypetree.arraycount: continue
        nested = (hasattr(mtypetree, "members") and mtypetree.members is not None)
        if nested:
            mret = block_subtree(mtypetree, attribstack + [mname])
            ret.update(mret)
    return ret


class Block(object):
    def __init__(self, io, mode, spydertype):
        assert io in ("antenna", "output"), antenna
        assert mode in ("push", "pull"), mode
        self.io = io
        self.mode = mode
        self.spydertype = spydertype
        spyderclass = getattr(Spyder, spydertype)
        self.spyderclass = spyderclass
        spydertypetree = spyderclass._typetree()
        assert isinstance(spydertypetree, spyder.core.typetreeclass)
        self.tree = block_subtree(spydertypetree)
        self.blockmap = {}  # identity mapping for all block elements; used in morphing
        self.attributes = {}
        for attribname, typename in self.tree.items():
            self.blockmap[attribname] = attribname
            h = Hook(self.mode, typename)
            h1, h2 = None, None
            if io == "antenna":
                h1, h2 = h, None
            else:
                h1, h2 = None, h
            a = Attribute(attribname, h1, h2)
            self.attributes[attribname] = a


def build_block(block):
    if block is None:
        return None
    io, mode, spydertype = block
    return Block(io, mode, spydertype)


def update_params_pullantennas(parameters, pullantennas):
    for a, pp in pullantennas:
        if a not in parameters:
            p2 = pp
            if isinstance(pp, tuple):
                p2 = (pp, None)
            parameters[a] = p2


class WorkerTemplate(object):

    _type = "worker"
    _builders = {
        "default": build_worker_default,
        "default_evio": build_worker_default_evio,
        "plain": build_worker_plain,
        "plain_evio": build_worker_plain_evio,
        "simplified": build_worker_simplified,
    }

    def __init__(self, beename, antennas, outputs, ev, paramnames, paramtypelist, block, tooltip, guiparams=None):
        self.beename = beename
        self.antennas = antennas
        self.outputs = outputs
        self.ev = ev
        self.paramnames = paramnames
        self.paramtypelist = paramtypelist
        self.block = build_block(block)
        self.forms = {}
        self.primary_instance = None
        self.tooltip = tooltip
        self.guiparams = guiparams

        for profile in self._builders:
            if profile == "simplified" and not support_simplified:
                continue
            builder = self._builders[profile]
            args = [beename, antennas, outputs, ev, paramnames, paramtypelist]
            if self._type == "worker":
                args.append(guiparams)

            attribs, mapping = builder(*args)

            if profile == "simplified" and (attribs, mapping) == (None, None):
                continue

            self.forms[profile] = attribs, mapping
        self.primary_instance = self.get_workerinstance()

    def get_workerinstance(self):
        # We don't need a deep copy if we don't modify the attributes in the profiles!!
        return WorkerInstance(self._type, self.forms, self.paramnames, self.paramtypelist, self.block, self.guiparams,
                              self.tooltip)


from ..segments.SegmentBuilder import \
    SegmentTemplate, SegmentVariableTemplate, \
    SegmentPushBufferTemplate, SegmentPullBufferTemplate


def build_workertemplate(worker_data):
    ev = worker_data.ev
    beename = worker_data.beename
    block = worker_data.block
    args = list(worker_data[:7]) + [worker_data.tooltip]

    if ev:
        return WorkerTemplate(*args, guiparams=worker_data.guiparams)

    elif beename == "variable":
        assert block is None
        return SegmentVariableTemplate(*args)

    elif beename == "push_buffer":
        assert block is None
        return SegmentPushBufferTemplate(*args)

    elif beename == "pull_buffer":
        assert block is None
        return SegmentPullBufferTemplate(*args)

    else:
        assert block is None
        return SegmentTemplate(*args)


from functools import partial


def modify_antenna_forms(antennas, guiparams, form_antenna):
    for antenna_name in antennas:
        form_antenna = getattr(form_antenna, antenna_name, None)
        if form_antenna is None:
            continue

        form_antenna.is_antenna = True
        if antenna_name not in guiparams:
            continue

        parameter = guiparams[antenna_name]
        if "name" in parameter and not hasattr(form_antenna, "name"):
            form_antenna.name = parameter["name"]


def make_form_manipulators(guiparams, manip):
    antennas = {}
    if guiparams is not None and "antennas" in guiparams:
        antennas = guiparams["antennas"]

    form_antennas = []
    for antenna_name in antennas:
        antenna = antennas[antenna_name]
        if antenna[0] != "pull":
            continue
        form_antennas.append(antenna_name)

    if manip is None and not len(form_antennas):
        return []
    if not len(form_antennas):
        return [manip]

    m = partial(modify_antenna_forms, form_antennas, guiparams.get("guiparams", {}))
    if manip is None:
        return [m]

    return [manip, m]


class WorkerBuilder(object):

    def __init__(self):
        self._workers = {}
        self._metaworkers = {}
        self._form_manipulators = {}

    def _build_worker(self, workername, worker):
        gui_params = worker.guiparams
        beename = gui_params["__beename__"]
        antennas = gui_params.get("antennas", {})
        outputs = gui_params.get("outputs", {})
        ev = gui_params.get("__ev__", [])
        block = gui_params.get("block", None)
        parameters = gui_params.get("parameters", {}).copy()
        pullantennas = get_param_pullantennas(antennas)
        update_params_pullantennas(parameters, pullantennas)
        paramnames, paramtypelist = get_paramtypelist(workername, parameters)
        # TODO finalise this
        return WorkerData(beename, antennas, outputs, ev, paramnames, paramtypelist, block, gui_params,
                          (worker.__doc__ or "").lstrip().rstrip())

    def _build_hivemapworker(self, workername, hivemap):
        from bee.types import stringtupleparser

        beename = workername
        antennas = {}
        outputs = {}

        if hivemap.io is not None:
            for io in hivemap.io:
                if io.mode is None or io.datatype is None:
                    print("Cannot register hivemapworker '%s': HivemapIO mode/type not completely defined" % workername)
                    return None

                hio = (io.mode, io.datatype)
                if io.io == "antenna":
                    antennas[io.io_id] = hio
                else:
                    outputs[io.io_id] = hio

        ev = ['everr', 'evexc', 'evin', 'evout']

        param_names, param_type_list = [], []
        if hivemap.parameters is not None:
            parameters = {}
            for parameter in hivemap.parameters:
                parameters[parameter.extern_id] = parameter.paramtypename

            pull_antennas = get_param_pullantennas(antennas)
            update_params_pullantennas(parameters, pull_antennas)
            param_names, param_type_list = get_paramtypelist(workername, parameters)

        # TODO support tooltip here
        block = None
        return WorkerData(beename, antennas, outputs, ev, param_names, param_type_list, block, {}, "")

    def build_worker(self, id_, worker):
        assert id_ not in self._workers

        worker_data = self._build_worker("worker " + id_, worker)
        paramtypelist = worker_data.paramtypelist
        if paramtypelist is None:
            return False  # some error in loading...

        worker_template = build_workertemplate(worker_data)
        self._workers[id_] = worker_template

        manipulator = None
        if hasattr(worker, "form") and callable(worker.form):
            manipulator = worker.form

        self._form_manipulators[id_] = make_form_manipulators(worker.guiparams, manipulator)
        return True

    def build_hivemapworker(self, id_, hivemapworker):
        assert id_ not in self._workers

        worker_data = self._build_hivemapworker("hivemapworker " + id_, hivemapworker)
        if worker_data is None:
            return False

        self._workers[id_] = build_workertemplate(worker_data)
        self._form_manipulators[id_] = []

        return True

    def get_block(self, id_):
        return self._workers[id_].block

    def remove_worker(self, id_):
        self._workers.pop(id_)

    def build_metaworker(self, id_, metaworker):
        assert id_ not in self._metaworkers

        meta_guiparams = {}
        member_order = None
        for key, value in metaworker.metaguiparams.items():

            if key == "_memberorder":
                member_order = value
                continue

            if key not in ("guiparams", "autocreate"):
                meta_guiparams[key] = value

        paramnames, paramtypelist = get_paramtypelist("metaworker " + id_, meta_guiparams)

        if paramtypelist is None:
            return False  # some error in loading...

        if member_order is not None:
            sorted_parameters = sorted(zip(paramnames, paramtypelist), key=partial(keyfunc, member_order))
            paramnames, paramtypelist = zip(*sorted_parameters)

        self._metaworkers[id_] = metaworker, paramnames, paramtypelist

        manipulator = None
        if hasattr(metaworker, "form") and callable(metaworker.form):
            manipulator = metaworker.form
        self._form_manipulators[id_] = make_form_manipulators(metaworker.metaguiparams, manipulator)

    def get_metaworker(self, id_):
        return self._metaworkers[id_]

    def remove_metaworker(self, id_):
        self._metaworkers.pop(id_)

    def build_worker_from_meta(self, metaworkername, metaparams):
        metaworker_data = self._metaworkers[metaworkername]
        metaworker, mparamnames, mparamtypelist = metaworker_data

        arglist = [metaparams.get(mparamname, None) for mparamname in mparamnames]
        args = parse_paramtypelist(mparamtypelist, arglist)
        mparams = dict(zip(mparamnames, args))

        workerclass = metaworker(**mparams)
        assert workerclass is not None, metaworkername

        worker_data = self._build_worker(metaworkername, workerclass)

        paramtypelist = worker_data.paramtypelist
        assert paramtypelist is not None

        worker = build_workertemplate(worker_data)

        manipulator = None
        if hasattr(workerclass, "form") and callable(workerclass.form):
            manipulator = workerclass.form

        key = metaworkername, freeze(mparams.items())
        self._form_manipulators[key] = make_form_manipulators(worker.guiparams, manipulator)

        return worker, mparamnames, mparamtypelist, mparams

    def get_workertemplate(self, id_):
        assert id_ in self._workers
        return self._workers[id_]

    def get_workerinstance(self, id_):
        assert id_ in self._workers
        return self._workers[id_].get_workerinstance()

    def has_worker(self, id_):
        return id_ in self._workers

    def has_metaworker(self, id_):
        return id_ in self._metaworkers

    def get_form_manipulators(self, workertype, metaparams):
        assert workertype in self._form_manipulators, workertype
        if metaparams is None:
            return self._form_manipulators[workertype]
        assert workertype in self._metaworkers
        key = workertype, freeze(metaparams.items())
        return self._form_manipulators[key]

    @staticmethod
    def get_droneinstance():
        return droneinstance

    @staticmethod
    def get_zeroinstance():
        return zeroinstance
