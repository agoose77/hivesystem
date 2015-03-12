from functools import partial

import sys, re

if sys.version_info[0] == 3:
    identifier = re.compile(r"^[^\d\W]\w*\Z", re.UNICODE)
else:
    identifier = re.compile(r"^[^\d\W]\w*\Z")


class CodeState(object):
    def __init__(self, name):
        self.name = name
        self.precode = """import bee
from bee.segments import *
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *
  """

        self.class_statement = "class %s(bee.worker):" % name
        self.place_statement = "def place(self):"

        self.classcode = ""
        self.placecode = ""


def cstrip(code):
    return code.rstrip(" ").rstrip("\n").rstrip("#")


def gen_transistor2(type_, segid, params, metaparams, codestate, m):
    if not type_.startswith("("): type_ = "'" + type_ + "'"
    codestate.classcode += "%s = transistor(%s)\n\n" % (segid, type_)
    if "triggerfunc" in params:
        tf = params["triggerfunc"]
        if tf is not None and len(tf.strip()):
            codestate.classcode += "%s = triggerfunc(%s)\n\n" % (tf, segid)


def gen_transistor(segid, params, metaparams, codestate, m):
    type_ = metaparams["type"].strip()
    gen_transistor2(type_, segid, params, metaparams, codestate, m)


def gen_weaver(segid, params, metaparams, codestate, m):
    inputs = {}
    for con in m.connections:
        if con.end.segid == segid:
            inp = con.end.io
            other = con.start.segid
            if inp in inputs:
                raise Exception("Weaver %s.%s cannot have more than one input" % (segid, inp))
            inputs[inp] = other
    count = 0
    intype = []
    while 1:
        count += 1
        k = "type%d" % count
        if k not in metaparams: break
        t = metaparams[k].strip()
        if len(t):
            intype.append(t)
    targets = []
    for nr, n in enumerate(range(len(intype))):
        inp = "inp%d" % (nr + 1)
        if inp not in inputs:
            raise Exception("Weaver %s.%s must have an input" % (segid, inp))
        targets.append(inputs[inp])

    line = "%s = weaver(%s, %s)\n\n" % (segid, tuple(intype), ", ".join(targets))
    codestate.classcode += line


def gen_unweaver(segid, params, metaparams, codestate, m):
    outputs = {}
    for con in m.connections:
        if con.start.segid == segid:
            outp = con.start.io
            other = con.end.segid
            if outp in outputs:
                raise Exception("Unweaver %s.%s cannot have more than one Output" % (segid, outp))
            outputs[outp] = other
    count = 0
    outtype = []
    while 1:
        count += 1
        k = "type%d" % count
        if k not in metaparams: break
        t = metaparams[k].strip()
        if len(t):
            outtype.append(t)
    targets = []
    for nr, n in enumerate(range(len(outtype))):
        outp = "outp%d" % (nr + 1)
        if outp not in outputs:
            raise Exception("Unweaver %s.%s must have an Output" % (segid, outp))
        targets.append(outputs[outp])

    line = "%s = unweaver(%s, %s)\n\n" % (segid, tuple(outtype), ", ".join(targets))
    codestate.classcode += line


def gen_antenna2(mode, type_, segid, params, metaparams, codestate, m):
    if not type_.startswith("("): type_ = "'" + type_ + "'"
    line = "%s = Antenna('%s', %s)\n\n" % (segid, mode, type_)
    codestate.classcode += line


def gen_push_antenna(segid, params, metaparams, codestate, m):
    type_ = metaparams["type"].strip()
    gen_antenna2("push", type_, segid, params, metaparams, codestate, m)


def gen_pull_antenna(segid, params, metaparams, codestate, m):
    type_ = metaparams["type"].strip()
    gen_antenna2("pull", type_, segid, params, metaparams, codestate, m)


def gen_output2(mode, type_, segid, params, metaparams, codestate, m):
    if not type_.startswith("("): type_ = "'" + type_ + "'"
    line = "%s = Output('%s', %s)\n" % (segid, mode, type_)
    codestate.classcode += line
    if type_ == "'trigger'":
        if "triggerfunc" in params:
            tf = params["triggerfunc"]
            if tf is not None and len(tf.strip()):
                codestate.classcode += "%s = triggerfunc(%s)\n\n" % (tf, segid)
    codestate.classcode += '\n'


def gen_push_output(segid, params, metaparams, codestate, m):
    type_ = metaparams["type"].strip()
    gen_output2("push", type_, segid, params, metaparams, codestate, m)


def gen_pull_output(segid, params, metaparams, codestate, m):
    type_ = metaparams["type"].strip()
    gen_output2("pull", type_, segid, params, metaparams, codestate, m)


def gen_variable2(type_, segid, params, metaparams, codestate, m):
    if not type_.startswith("("): type_ = "'" + type_ + "'"
    codestate.classcode += "%s = variable(%s)\n" % (segid, type_)
    if "val" in params and params["val"] not in ("", None):
        value = params["val"]
        k = "startvalue"
        if "is_parameter" in params and params["is_parameter"] == "True":
            k = "Parameter"
        codestate.classcode += "%s(%s, %s)\n\n" % (k, segid, value)
    elif "is_parameter" in params and params["is_parameter"] == "True":
        codestate.classcode += "Parameter(%s)\n\n" % segid
    else:
        codestate.classcode += "\n"


def gen_variable(segid, params, metaparams, codestate, m):
    type_ = metaparams["type"].strip()
    gen_variable2(type_, segid, params, metaparams, codestate, m)


def gen_push_buffer2(type_, segid, params, metaparams, codestate, m):
    if not type_.startswith("("): type_ = "'" + type_ + "'"
    codestate.classcode += "%s = buffer('push', %s)\n\n" % (segid, type_)
    if "val" in params and params["val"] not in ("", None):
        value = params["val"]
        k = "startvalue"
        if "is_parameter" in params and params["is_parameter"] == "True":
            k = "Parameter"
        codestate.classcode += "%s(%s, %s)\n\n" % (k, segid, value)
    elif "is_parameter" in params and params["is_parameter"] == "True":
        codestate.classcode += "Parameter(%s)\n\n" % segid
    else:
        codestate.classcode += "\n"
    if "triggerfunc" in params:
        tf = params["triggerfunc"]
        if tf is not None and len(tf.strip()):
            codestate.classcode += "%s = triggerfunc(%s)\n\n" % (tf, segid)


def gen_pull_buffer(segid, params, metaparams, codestate, m):
    type_ = metaparams["type"].strip()
    gen_pull_buffer2(type_, segid, params, metaparams, codestate, m)


def gen_pull_buffer2(type_, segid, params, metaparams, codestate, m):
    if not type_.startswith("("): type_ = "'" + type_ + "'"
    codestate.classcode += "%s = buffer('pull', %s)\n\n" % (segid, type_)
    if "val" in params and params["val"] not in ("", None):
        value = params["val"]
        k = "startvalue"
        if "is_parameter" in params and params["is_parameter"] == "True":
            k = "Parameter"
        codestate.classcode += "%s(%s, %s)\n\n" % (k, segid, value)
    elif "is_parameter" in params and params["is_parameter"] == "True":
        codestate.classcode += "Parameter(%s)\n\n" % segid
    else:
        codestate.classcode += "\n"
    if "triggerfunc" in params:
        tf = params["triggerfunc"]
        if tf is not None and len(tf.strip()):
            codestate.classcode += "%s = triggerfunc(%s)\n\n" % (tf, segid)


def gen_push_buffer(segid, params, metaparams, codestate, m):
    type_ = metaparams["type"].strip()
    gen_push_buffer2(type_, segid, params, metaparams, codestate, m)


def gen_modifier(segid, params, metaparams, codestate, m):
    code = params.get("code", "pass")
    if code is None or len(code.strip()) == 0: code = "pass"
    c = "@modifier\n"
    c += "def %s(self):\n" % segid
    indent = 2
    ind = "\n" + " " * indent
    c += ind[1:] + ind.join(cstrip(code).split("\n"))
    codestate.classcode += c + "\n\n"


def gen_operator(segid, params, metaparams, codestate, m):
    intype = metaparams["intype"].strip()
    if not intype.startswith("("): intype = '"' + intype + '"'
    outtype = metaparams["outtype"].strip()
    if not outtype.startswith("("): outtype = '"' + outtype + '"'
    code = params.get("code", "pass")
    if code is None or len(code.strip()) == 0: code = "pass"
    funcname = "operator_func_%s" % segid
    c = "def %s(self):\n" % funcname
    indent = 2
    ind = "\n" + " " * indent
    c += ind[1:] + ind.join(cstrip(code).split("\n"))
    codestate.precode += c + "\n\n"
    codestate.classcode += "%s = operator(%s, %s, %s)\n\n" % (segid, funcname, intype, outtype)


def gen_custom_import_code(segid, params, metaparams, codestate, m):
    code = params.get("code", "")
    if code is None or len(code.strip()) == 0: return
    codestate.precode += "\n" + cstrip(code) + "\n\n"


def gen_custom_class_code(segid, params, metaparams, codestate, m):
    code = params.get("code", "")
    if code is None or len(code.strip()) == 0: return
    codestate.classcode += "\n" + cstrip(code) + "\n\n"


def gen_custom_place_code(segid, params, metaparams, codestate, m):
    code = params.get("code", "")
    if code is None or len(code.strip()) == 0: return
    codestate.placecode += "\n" + cstrip(code) + "\n\n"


generators = {
    "transistor.transistor": gen_transistor,
    "transistor.transistor_int": partial(gen_transistor2, "int"),
    "transistor.transistor_float": partial(gen_transistor2, "float"),
    "transistor.transistor_bool": partial(gen_transistor2, "bool"),
    "transistor.transistor_str": partial(gen_transistor2, "str"),
    "transistor.transistor_id": partial(gen_transistor2, "id"),

    "unweaver.unweaver": gen_unweaver,
    "weaver.weaver": gen_weaver,
    "Antenna.push_antenna": gen_push_antenna,
    "Antenna.push_antenna_trigger": partial(gen_antenna2, "push", "trigger"),
    "Antenna.push_antenna_int": partial(gen_antenna2, "push", "int"),
    "Antenna.push_antenna_float": partial(gen_antenna2, "push", "float"),
    "Antenna.push_antenna_bool": partial(gen_antenna2, "push", "bool"),
    "Antenna.push_antenna_str": partial(gen_antenna2, "push", "str"),
    "Antenna.push_antenna_id": partial(gen_antenna2, "push", "id"),
    "Antenna.pull_antenna": gen_pull_antenna,
    "Antenna.pull_antenna_int": partial(gen_antenna2, "pull", "int"),
    "Antenna.pull_antenna_float": partial(gen_antenna2, "pull", "float"),
    "Antenna.pull_antenna_bool": partial(gen_antenna2, "pull", "bool"),
    "Antenna.pull_antenna_str": partial(gen_antenna2, "pull", "str"),
    "Antenna.pull_antenna_id": partial(gen_antenna2, "pull", "id"),

    "Output.push_output": gen_push_output,
    "Output.push_output_trigger": partial(gen_output2, "push", "trigger"),
    "Output.push_output_int": partial(gen_output2, "push", "int"),
    "Output.push_output_float": partial(gen_output2, "push", "float"),
    "Output.push_output_bool": partial(gen_output2, "push", "bool"),
    "Output.push_output_str": partial(gen_output2, "push", "str"),
    "Output.push_output_id": partial(gen_output2, "push", "id"),
    "Output.pull_output": gen_pull_output,
    "Output.pull_output_int": partial(gen_output2, "pull", "int"),
    "Output.pull_output_float": partial(gen_output2, "pull", "float"),
    "Output.pull_output_bool": partial(gen_output2, "pull", "bool"),
    "Output.pull_output_str": partial(gen_output2, "pull", "str"),
    "Output.pull_output_id": partial(gen_output2, "pull", "id"),

    "variable.variable": gen_variable,
    "variable.variable_int": partial(gen_variable2, "int"),
    "variable.variable_float": partial(gen_variable2, "float"),
    "variable.variable_bool": partial(gen_variable2, "bool"),
    "variable.variable_str": partial(gen_variable2, "str"),
    "variable.variable_id": partial(gen_variable2, "id"),

    "modifier.modifier": gen_modifier,
    "operator.operator": gen_operator,

    "buffer.push_buffer": gen_push_buffer,
    "buffer.push_buffer_int": partial(gen_push_buffer2, "int"),
    "buffer.push_buffer_float": partial(gen_push_buffer2, "float"),
    "buffer.push_buffer_bool": partial(gen_push_buffer2, "bool"),
    "buffer.push_buffer_str": partial(gen_push_buffer2, "str"),
    "buffer.push_buffer_id": partial(gen_push_buffer2, "id"),

    "buffer.pull_buffer": gen_pull_buffer,
    "buffer.pull_buffer_int": partial(gen_pull_buffer2, "int"),
    "buffer.pull_buffer_float": partial(gen_pull_buffer2, "float"),
    "buffer.pull_buffer_bool": partial(gen_pull_buffer2, "bool"),
    "buffer.pull_buffer_str": partial(gen_pull_buffer2, "str"),
    "buffer.pull_buffer_id": partial(gen_pull_buffer2, "id"),

    "custom_code.custom_import_code": gen_custom_import_code,
    "custom_code.custom_class_code": gen_custom_class_code,
    "custom_code.custom_place_code": gen_custom_place_code,


}


def _find_segment(segid, segments):
    for seg in segments:
        if seg.segid == segid:
            return seg
    raise KeyError(segid)


def _add_segment(seg, segments, allsegments, segids=None):
    if segids is None: segids = []
    segid = seg.segid
    if segid in segids: return
    if seg.segtype.endswith(".weaver"):
        for con in m.connections:
            if con.end.segid == segid:
                other = allsegments[con.start.segid]
                if other not in segids: _add_segment(other, segments, allsegments, segids)
    elif seg.segtype.endswith(".unweaver"):
        for con in m.connections:
            if con.start.segid == segid:
                other = allsegments[con.end.segid]
                if other not in segids: _add_segment(other, segments, allsegments, segids)
    segids.append(segid)
    segments.append(seg)


def workergen(name, m):
    codestate = CodeState(name)
    if m.docstring is not None:
        codestate.classcode += "\"\"\"\n" + m.docstring + "\"\"\"\n"

    # Check for duplicate segids
    segids0 = set()

    #if m.docstring is not None:
     #   codestate.classcode += "\"\"\"\n" + m.docstring + "\"\"\"\n"

    def check_segid(segid):
        if re.match(identifier, segid) is None:
            raise Exception("Invalid segment ID '%s'" % segid)
        if segid in segids0:
            raise Exception("Duplicate segment ID '%s'" % segid)
        segids0.add(segid)

    for seg in m.segments:
        segid = seg.segid
        check_segid(segid)
        if seg.parameters is not None:
            for par in seg.parameters:
                if par.pname == "triggerfunc":
                    v = par.pvalue
                    if v is not None and len(v.strip()):
                        check_segid(v)


    #Reshuffle segment order in case of weavers/unweavers
    allsegments = dict([(seg.segid, seg) for seg in m.segments])
    segments = []
    for seg in m.segments:
        _add_segment(seg, segments, allsegments)

    #Generate code for segments
    for seg in segments:
        assert seg.segtype.startswith("segments.")
        segtype = seg.segtype[len("segments."):]
        params = {}
        if seg.parameters is not None:
            params = dict([(p.pname, p.pvalue) for p in seg.parameters])
        metaparams = {}
        if seg.metaparameters is not None:
            metaparams = dict([(p.pname, p.pvalue) for p in seg.metaparameters])
        generators[segtype](seg.segid, params, metaparams, codestate, m)

    #segid-to-type dict
    tdic = {}
    for seg in segments:
        type_ = seg.segtype.split(".")[-1]
        tdic[seg.segid] = type_

    #Generate code for connections
    for connection_name in m.connections:
        start_segmnent_id = connection_name.start.segid
        end_segment_id = connection_name.end.segid
        t1 = tdic[start_segmnent_id]
        t2 = tdic[end_segment_id]
        seg1 = allsegments[start_segmnent_id]
        seg2 = allsegments[end_segment_id]

        source, target = start_segmnent_id, end_segment_id
        arg = None
        k = "connect"
        if t1.startswith("push_antenna"):
            if t1 == "push_antenna_trigger" or t1 == "push_antenna" and seg1.type == "trigger":
                #Special case: ("push", "trigger") may send triggers
                k = "trigger"
            else:
                pass
        elif t1.startswith("pull_antenna"):
            pass
        elif t1.startswith("transistor"):
            pass
        elif t1 == "weaver":
            pass
        elif t1 == "unweaver":
            continue
        elif t1 == "test":
            k = "trigger"
        elif t1 == "modifier":
            k = "trigger"
        elif t1.startswith("variable"):
            if connection_name.start.io == "pre_update":
                k = "pretrigger"
                arg = "update"
            elif connection_name.start.io == "pre_output":
                k = "pretrigger"
            elif connection_name.start.io == "on_update":
                k = "trigger"
            elif connection_name.start.io == "on_output":
                k = "trigger"
                arg = "Output"
        elif t1.startswith("push_buffer"):
            if connection_name.start.io == "pre_update":
                k = "pretrigger"
            elif connection_name.start.io == "on_update":
                k = "trigger"
        elif t1.startswith("pull_buffer"):
            if connection_name.start.io == "pre_output":
                k = "pretrigger"
            elif connection_name.start.io == "on_output":
                k = "trigger"
        else:
            raise Exception(t1)

        if t2 == "weaver": continue

        if arg is None:
            line = '%s(%s, %s)\n' % (k, source, target)
        else:
            line = '%s(%s, %s, "%s")\n' % (k, source, target, arg)
        codestate.classcode += line
        #Join code
    if codestate.classcode == "" and codestate.placecode == "":
        codestate.classcode = "pass"

    code = codestate.precode + "\n"
    code += codestate.class_statement + "\n"

    indent = 2
    ind = "\n" + " " * indent
    code += ind[1:] + ind.join(codestate.classcode.split("\n"))

    if len(codestate.placecode):
        code += ind + codestate.place_statement
        indent = 4
        ind = "\n" + " " * indent
        code += ind[1:] + ind.join(codestate.placecode.split("\n"))

    return code
