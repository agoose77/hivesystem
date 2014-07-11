from __future__ import print_function, absolute_import

from ..HGui import Attribute, Hook
from ..worker.WorkerBuilder import WorkerMapping


def build_segment_default(beename, antennas, outputs, ev, paramnames, paramtypelist):
    mapping = WorkerMapping()
    attribs = []
    attrs = [(pname, "antenna", pval) for pname, pval in antennas.items()] + \
            [(pname, "output", pval) for pname, pval in outputs.items()]
    attrs.sort(key=lambda i: i[0])

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
        )
        if io == "antenna":
            if pname in ("output", "update"):
                inmap[pname] = None
                continue
        if io == "output":
            if pname.startswith("on_"):
                outmap[pname] = None
                continue
            if pname.startswith("pre_"):
                outmap[pname] = None
                continue
        attribs.append(a)
    for paramname in paramnames:
        pmap[paramname] = None
    mapping.inmap, mapping.outmap, mapping.pmap = inmap, outmap, pmap
    return attribs, mapping


def build_segment_minimal(beename, antennas, outputs, ev, paramnames, paramtypelist):
    mapping = WorkerMapping()
    attribs = []
    attrs = [(pname, "antenna", pval) for pname, pval in antennas.items()] + \
            [(pname, "output", pval) for pname, pval in outputs.items()]
    attrs.sort(key=lambda i: i[0])

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
        )
        if io == "antenna":
            if pname in ("output", "update", "inp"):
                inmap[pname] = None
                continue
        if io == "output":
            if pname == "outp":
                outmap[pname] = None
                continue
            if pname.startswith("on_"):
                outmap[pname] = None
                continue
            if pname.startswith("pre_"):
                outmap[pname] = None
                continue
        attribs.append(a)
    for paramname in paramnames:
        pmap[paramname] = None
    mapping.inmap, mapping.outmap, mapping.pmap = inmap, outmap, pmap
    return attribs, mapping


def build_segment_full(beename, antennas, outputs, ev, paramnames, paramtypelist):
    mapping = WorkerMapping()
    attribs = []
    attrs = [(pname, "antenna", pval) for pname, pval in antennas.items()] + \
            [(pname, "output", pval) for pname, pval in outputs.items()]
    attrs.sort(key=lambda i: i[0])

    inmap, outmap, pmap = mapping.inmap, mapping.outmap, mapping.pmap
    #print(beename, antennas, paramnames)
    d = dict(zip(paramnames, paramtypelist))
    if "val" in paramnames and "val" in d:
        valuetype = d["val"][0][0]
        pmap["val"] = "value"
        attribs.append(Attribute("value", type=valuetype))

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
        )
        attribs.append(a)
    for paramname in paramnames:
        if paramname not in pmap:
            pmap[paramname] = None
    mapping.inmap, mapping.outmap, mapping.pmap = inmap, outmap, pmap
    return attribs, mapping


from ..worker.WorkerBuilder import WorkerTemplate


class SegmentTemplate(WorkerTemplate):
    _type = "segment"
    _builders = {
        "default": build_segment_default,
        "full": build_segment_full,
    }


from ..HGui import Attribute


def add_value(attribs, mapping, paramnames, paramtypelist):
    inmap, outmap, pmap = mapping.inmap, mapping.outmap, mapping.pmap
    d = dict(zip(paramnames, paramtypelist))
    if "val" in paramnames and "val" in d:
        valuetype = d["val"][0][0]
        pmap["val"] = "value"
        attribs.insert(0, Attribute("value", type=valuetype))

    mapping.inmap, mapping.outmap, mapping.pmap = inmap, outmap, pmap
    return attribs, mapping


def add_output(attribs, mapping, outputs):
    inmap, outmap, pmap = mapping.inmap, mapping.outmap, mapping.pmap

    pname = "outp"
    type_ = outputs[pname][1]
    h = Hook("pull", type_)
    a = Attribute(
        pname,
        None, h,
    )
    attribs.append(a)
    outmap[pname] = pname

    mapping.inmap, mapping.outmap, mapping.pmap = inmap, outmap, pmap
    return attribs, mapping


def add_trigger_output(attribs, mapping, pname):
    inmap, outmap, pmap = mapping.inmap, mapping.outmap, mapping.pmap

    h = Hook("push", "trigger")
    a = Attribute(
        pname,
        None, h,
    )
    attribs.append(a)
    outmap[pname] = pname

    mapping.inmap, mapping.outmap, mapping.pmap = inmap, outmap, pmap
    return attribs, mapping


def add_input(attribs, mapping, antennas):
    inmap, outmap, pmap = mapping.inmap, mapping.outmap, mapping.pmap

    pname = "inp"
    type_ = antennas[pname][1]
    h = Hook("push", type_)
    a = Attribute(
        pname,
        h, None,
    )
    attribs.append(a)
    inmap[pname] = pname

    mapping.inmap, mapping.outmap, mapping.pmap = inmap, outmap, pmap
    return attribs, mapping


def add_trigger_input(attribs, mapping, pname):
    inmap, outmap, pmap = mapping.inmap, mapping.outmap, mapping.pmap

    h = Hook("push", "trigger")
    a = Attribute(
        pname,
        h, None,
    )
    attribs.append(a)
    inmap[pname] = pname

    mapping.inmap, mapping.outmap, mapping.pmap = inmap, outmap, pmap
    return attribs, mapping


def build_segment_parameter(beename, antennas, outputs, ev, paramnames, paramtypelist):
    attribs, mapping = build_segment_default(
        beename, antennas, outputs, ev, paramnames, paramtypelist
    )
    attribs, mapping = add_value(attribs, mapping, paramnames, paramtypelist)
    return attribs, mapping


def build_variable_parameter(beename, antennas, outputs, ev, paramnames, paramtypelist):
    attribs, mapping = build_segment_minimal(
        beename, antennas, outputs, ev, paramnames, paramtypelist
    )
    attribs, mapping = add_value(attribs, mapping, paramnames, paramtypelist)
    return attribs, mapping


def build_variable_input(beename, antennas, outputs, ev, paramnames, paramtypelist):
    attribs, mapping = build_segment_minimal(
        beename, antennas, outputs, ev, paramnames, paramtypelist
    )
    attribs, mapping = add_input(attribs, mapping, antennas)
    attribs, mapping = add_trigger_output(attribs, mapping, "on_update")
    return attribs, mapping


def build_variable_parameter_input(beename, antennas, outputs, ev, paramnames, paramtypelist):
    attribs, mapping = build_segment_minimal(
        beename, antennas, outputs, ev, paramnames, paramtypelist
    )
    attribs, mapping = add_value(attribs, mapping, paramnames, paramtypelist)
    attribs, mapping = add_input(attribs, mapping, antennas)
    attribs, mapping = add_trigger_output(attribs, mapping, "on_update")
    return attribs, mapping


def build_variable_output(beename, antennas, outputs, ev, paramnames, paramtypelist):
    attribs, mapping = build_segment_minimal(
        beename, antennas, outputs, ev, paramnames, paramtypelist
    )
    attribs, mapping = add_output(attribs, mapping, outputs)
    attribs, mapping = add_trigger_output(attribs, mapping, "pre_output")
    return attribs, mapping


def build_variable_parameter_output(beename, antennas, outputs, ev, paramnames, paramtypelist):
    attribs, mapping = build_segment_minimal(
        beename, antennas, outputs, ev, paramnames, paramtypelist
    )
    attribs, mapping = add_value(attribs, mapping, paramnames, paramtypelist)
    attribs, mapping = add_output(attribs, mapping, outputs)
    attribs, mapping = add_trigger_output(attribs, mapping, "pre_output")
    return attribs, mapping


def build_pushbuffer_input(beename, antennas, outputs, ev, paramnames, paramtypelist):
    attribs, mapping = build_segment_default(
        beename, antennas, outputs, ev, paramnames, paramtypelist
    )
    attribs, mapping = add_trigger_output(attribs, mapping, "on_update")
    return attribs, mapping


def build_pushbuffer_parameter_input(beename, antennas, outputs, ev, paramnames, paramtypelist):
    attribs, mapping = build_segment_default(
        beename, antennas, outputs, ev, paramnames, paramtypelist
    )
    attribs, mapping = add_value(attribs, mapping, paramnames, paramtypelist)
    attribs, mapping = add_trigger_output(attribs, mapping, "on_update")
    return attribs, mapping


def build_pullbuffer_output(beename, antennas, outputs, ev, paramnames, paramtypelist):
    attribs, mapping = build_segment_default(
        beename, antennas, outputs, ev, paramnames, paramtypelist
    )
    attribs, mapping = add_trigger_output(attribs, mapping, "pre_output")
    return attribs, mapping


def build_pullbuffer_parameter_output(beename, antennas, outputs, ev, paramnames, paramtypelist):
    attribs, mapping = build_segment_default(
        beename, antennas, outputs, ev, paramnames, paramtypelist
    )
    attribs, mapping = add_value(attribs, mapping, paramnames, paramtypelist)
    attribs, mapping = add_trigger_output(attribs, mapping, "pre_output")
    return attribs, mapping


class SegmentVariableTemplate(SegmentTemplate):
    _type = "segment-variable"
    _builders = {
        "default": build_segment_default,
        "parameter": build_segment_parameter,
        "full": build_segment_full,

        "minimal": build_segment_minimal,
        "parameter2": build_variable_parameter,
        "input": build_variable_input,
        "parameter_input": build_variable_parameter_input,
        "output": build_variable_output,
        "parameter_output": build_variable_parameter_output,
    }


class SegmentPushBufferTemplate(SegmentTemplate):
    _type = "segment-pushbuffer"
    _builders = {
        "default": build_segment_default,
        "full": build_segment_full,
        "parameter": build_segment_parameter,
        "input": build_pushbuffer_input,
        "parameter_input": build_pushbuffer_parameter_input,
    }


class SegmentPullBufferTemplate(SegmentTemplate):
    _type = "segment-pullbuffer"
    _builders = {
        "default": build_segment_default,
        "full": build_segment_full,
        "parameter": build_segment_parameter,
        "output": build_pullbuffer_output,
        "parameter_output": build_pullbuffer_parameter_output,
    }
