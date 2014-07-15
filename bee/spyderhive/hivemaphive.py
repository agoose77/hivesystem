import libcontext
import spyder, Spyder

from .. import connect, frame
from .. import resolvelist
from .spyderhive import SpyderMethod, SpyderConverter, spyderframe, spyderhive, spyderinithive
from .spydermaphive import spydermapframe

from ..types import stringtupleparser, boolparser, spyderparser
from .. import antenna, output, \
    parameter as _bee_parameter, get_parameter as _bee_get_parameter, \
    attribute as _bee_attribute
import os


def build_hivemap(hm, *args, **kwargs):
    d = {}
    __makehivemap_workers__ = {}
    __makehivemap_drones__ = {}
    __hmworkerclasslist__ = set()
    __smworkerclasslist__ = set()
    __hmworkerlist__ = set()
    __workers_and_drones__ = {}
    __injections__ = {}

    __hop_in_id_to_name__ = {}
    __hop_out_id_to_name__ = {}

    if hm.wasps is not None:

        for wasp in hm.wasps:
            injected = stringtupleparser(wasp.injected)
            if wasp.target not in __injections__:
                __injections__[wasp.target] = []

            __injections__[wasp.target].append((wasp.targetparam, (injected, wasp.sting, wasp.accumulate)))

    for worker in hm.workers:
        wt = worker.workertype

        # Don't create rerouters
        if wt in ("sparta.rerouters.hop_in", "sparta.rerouters.hop_out"):
            for _param in worker.parameters:
                if _param.pname == "name_":
                    break

            else:
                raise ValueError("Hop worker has no name parameter")

            if wt == "sparta.rerouters.hop_in":
                hop_dict = __hop_in_id_to_name__
            else:
                hop_dict = __hop_out_id_to_name__

            hop_dict[worker.workerid] = _param.pvalue
            continue

        __workers_and_drones__[worker.workerid] = ("worker", worker)

        if wt in __makehivemap_workers__:
            continue

        lastdot = wt.rindex(".")
        if wt.find(":") > -1:  # hivemapworker
            modname, filename = wt.split(":")

        elif wt.find("#") > -1:  # spydermapworker
            modname, filename = wt.split("#")

        else:  # programmatic worker or worker-like hive
            modname = wt[:lastdot]

        workername = wt[lastdot + 1:]
        __makehivemap_worker0 = {}
        __makehivemap_worker00__ = __import__(modname, __makehivemap_worker0, __makehivemap_worker0, [workername])


        if wt.find(":") > -1 or wt.find("#") > -1:  # hivemapworker/spydermapworker
            f = __makehivemap_worker00__.__file__
            motif = ""
            if f.startswith("//"):
                f = f[2:]
                motif = "//"
            filedir = motif + os.path.split(f)[0]

        if wt.find(":") > -1:  # hivemapworker
            classname, _ = filename.split(".")
            if filedir == "":
                hmwfilename = filename
            else:
                hmwfilename = os.path.join(filedir, filename)

            hivemap = Spyder.Hivemap.fromfile(hmwfilename)
            __makehivemap_workers__[wt] = type(classname, (hivemapframe,), {"hivemap": hivemap})
            __hmworkerclasslist__.add(wt)

        elif wt.find("#") > -1:  # spydermapworker
            classname, _ = filename.split(".")
            if filedir == "":
                smwfilename = filename
            else:
                smwfilename = os.path.join(filedir, filename)
            spydermap = Spyder.Spydermap.fromfile(smwfilename)
            __makehivemap_workers__[wt] = \
                type(classname, (spydermapframe,), {"spydermap": spydermap})
            __smworkerclasslist__.add(wt)

        else:  # programmatic worker or worker-like hive
            __makehivemap_workers__[wt] = getattr(__makehivemap_worker00__, workername)

    if hm.drones is not None:
        for drone in hm.drones:
            __workers_and_drones__[drone.droneid] = ("drone", drone)
            dt = drone.dronetype
            if dt in __makehivemap_drones__:
                continue

            lastdot = dt.rindex(".")
            modname = dt[:lastdot]
            dronename = dt[lastdot + 1:]
            __makehivemap_drone0 = {}
            __makehivemap_drone00__ = __import__(modname, __makehivemap_drone0, __makehivemap_drone0, [dronename])
            __makehivemap_drones__[dt] = getattr(__makehivemap_drone00__, dronename)


    class maphive(frame):
        __makehivemap_worker = None
        locals()['__doc__'] = hm.docstring
        if hm.attributes is not None:
            _attr = None
            for _attr in hm.attributes:
                if _attr.attrtypename in ("str", "id"):
                    _attr_val = _attr.attrvalue

                elif _attr.attrtypename == "int":
                    _attr_val = int(_attr.attrvalue)

                elif _attr.attrtypename == "float":
                    _attr_val = float(_attr.attrvalue)

                elif _attr.attrtypename == "bool":
                    _attr_val = boolparser(_attr.attrvalue)

                else:
                    _attr_val = spyderparser(_attr.attrtypename, _attr.attrvalue)

                _attr_var = "_" + _attr.attr_id
                locals()[_attr_var] = _attr_val
                locals()[_attr.attr_id] = _bee_attribute(_attr_var)
                del _attr_val, _attr_var

            del _attr

        if hm.partbees is not None:
            _part = None

            for _part in hm.partbees:
                _target = locals()[_part.bee_id]
                _ppart = _part.part

                if isinstance(_target, _bee_attribute):
                    try:
                        _ppart = int(_ppart)

                    except ValueError:
                        pass

                    locals()[_part.part_id] = _bee_attribute(*(_target.args + (_ppart,)))

                else:
                    try:
                        _ppart = int(_ppart)
                        locals()[_part.part_id] = _target[_ppart]

                    except ValueError:
                        locals()[_part.part_id] = getattr(_target, _ppart)

                del _target, _ppart

            del _part

        if hm.pyattributes is not None:
            _attr = None

            for _attr in hm.pyattributes:
                if _attr.code_variable is not None and len(_attr.code_variable):
                    _execdic = {}
                    try:
                        exec(_attr.code, {}, _execdic)

                    except:
                        print("*" * 80 + "\n" + _attr.code + "\n" + "*" * 80 + "\n")
                        print(_attr)
                        raise

                    _attr_val = _execdic[_attr.code_variable]
                    del _execdic

                else:
                    try:
                        _attr_val = eval(_attr.code, {}, {})

                    except:
                        try:
                            exec(_attr.code, {}, {})
                            _attr_val = None

                        except:
                            print("*" * 80 + "\n" + _attr.code + "\n" + "*" * 80 + "\n")
                            raise

                _attr_var = "*" + _attr.attr_id
                locals()[_attr_var] = _attr_val
                locals()[_attr.attr_id] = _bee_attribute(_attr_var)
                del _attr_val, _attr_var

            del _attr

        if hm.parameters is not None:
            _param = None
            for _param in hm.parameters:
                _paramtypename = stringtupleparser(_param.paramtypename)
                if _param.gui_defaultvalue is not None and len(_param.gui_defaultvalue):
                    locals()[_param.extern_id] = _bee_parameter(_paramtypename, _param.gui_defaultvalue)

                else:
                    locals()[_param.extern_id] = _bee_parameter(_paramtypename)

                locals()[_param.intern_id] = _bee_get_parameter(_param.extern_id)

                del _paramtypename

            del _param

        _wdids = sorted(list(__workers_and_drones__.keys()))
        _wdids = [_wdid for _wdid in _wdids if _wdid not in __injections__] + \
                 [_wdid for _wdid in _wdids if _wdid in __injections__]

        for _wdid in _wdids:
            __inject_dict = {}

            if _wdid in __injections__:
                for _target in __injections__[_wdid]:
                    _t1, _sting, _accumulate = _target[1]
                    _wasp = locals()[_t1]
                    if _sting:
                        if isinstance(_wasp, _bee_attribute):
                            _wasp = _bee_attribute(*(_wasp.args + ("sting", "__call__")))

                        elif isinstance(_wasp, _bee_parameter):
                            _wasp = _bee_get_parameter(_t1).sting()

                        else:
                            _wasp = _wasp.sting()

                    if _accumulate:
                        if _target[0] not in __inject_dict:
                            __inject_dict[_target[0]] = resolvelist()

                        __inject_dict[_target[0]].append(_wasp)
                        _inj = "__inject_" + _wdid + _target[0] + "_%05d" % len(__inject_dict[_target[0]])

                    else:
                        __inject_dict[_target[0]] = _wasp
                        _inj = "__inject_" + _wdid + _target[0]

                    if _sting:
                        locals()[_inj] = _wasp

                    del _target, _wasp, _sting, _accumulate, _t1, _inj

            _wdtype, _wd = __workers_and_drones__[_wdid]

            if _wdtype == "worker":
                _worker = _wd

                if _worker.metaparameters is not None:
                    _mp = __makehivemap_workers__[_worker.workertype].metaguiparams
                    metaparamdict = dict([(_p.pname, _p.pvalue) for _p in _worker.metaparameters])
                    for _k in list(metaparamdict.keys()):
                        if _k in _mp and _mp[_k] == "type":
                            metaparamdict[_k] = stringtupleparser(metaparamdict[_k])

                        if metaparamdict[_k] == "None":
                            metaparamdict[_k] = None

                    __makehivemap_worker = __makehivemap_workers__[_worker.workertype](**metaparamdict)
                    del _k

                else:
                    __makehivemap_worker = __makehivemap_workers__[_worker.workertype]

                __makehivemap_p = {}
                _p = __makehivemap_worker.guiparams
                if _worker.parameters is not None:
                    _param = None

                    for _param in _worker.parameters:
                        _v = _param.pvalue
                        if _param.pname in _p and _p[_param.pname] == "type":
                            _v = stringtupleparser(_v)

                        if _v == "None":
                            _v = None

                        __makehivemap_p[_param.pname] = _v
                        del _v

                    del _param

                __makehivemap_p.update(__inject_dict)
                locals()[_worker.workerid] = __makehivemap_worker(**__makehivemap_p)
                if _worker.workertype in __hmworkerclasslist__:
                    locals()[_worker.workerid].hmworkername = _worker.workerid
                    __hmworkerlist__.add(_worker.workerid)

                elif _worker.workertype in __smworkerclasslist__:
                    locals()[_worker.workerid].hmworkername = _worker.workerid

                del _worker, __makehivemap_worker, __makehivemap_p, _p

            elif _wdtype == "drone":
                _drone = _wd
                _params = []
                _p = None
                if _drone.parameters is not None:
                    _params = [eval(_p) for _p in _drone.parameters if _p != ""]

                __makehivemap_drone = __makehivemap_drones__[_drone.dronetype]
                locals()[_drone.droneid] = __makehivemap_drone(*_params, **__inject_dict)
                del _drone, __makehivemap_drone, _params, _p

            else:
                raise ValueError(_wdtype)

            del _wdtype, _wd
            del __inject_dict

        _hop_in_proxies = {}
        _hop_out_clients = {}

        """
         for _param in _worker.parameters:
                        _v = _param.pvalue
                        if _param.pname in _p and _p[_param.pname] == "type":
                            _v = stringtupleparser(_v)

                        if _v == "None":
                            _v = None

                        __makehivemap_p[_param.pname] = _v
                        del _v


        """

        _hm_workers = list(__hmworkerlist__) + list(__hop_in_id_to_name__) + list(__hop_out_id_to_name__)

        for _con in hm.connections:

            _src = (_con.start.workerid, _con.start.io)
            if _src[0] in _hm_workers:
                _src = (_src[0], "hivemap", _src[1])

            _tar = (_con.end.workerid, _con.end.io)
            if _tar[0] in _hm_workers:
                _tar = (_tar[0], "hivemap", _tar[1])

            # Register hop_in clients
            if _con.end.workerid in __hop_in_id_to_name__:
                _hop_name = __hop_in_id_to_name__[_con.end.workerid]
                _hop_in_proxies[_hop_name] = _src
                continue

            # Register hop_out clients
            elif _con.start.workerid in __hop_out_id_to_name__:
                _hop_name = __hop_out_id_to_name__[_con.start.workerid]
                _hop_out_clients.setdefault(_hop_name, []).append(_tar)
                continue

            connect(_src, _tar)

        del _hm_workers

        # Establish proxy connections
        for _hop_id, _in_source in _hop_in_proxies.items():
            try:
                _out_clients = _hop_out_clients[_hop_id]

            except KeyError:
                continue

            for _client in _out_clients:
                connect(_in_source, _client)
                del _client

            del _out_clients
            del _hop_id
            del _in_source

        del _hop_out_clients
        del _hop_in_proxies
#
        if hm.io is not None:
            for _io in hm.io:
                _antenna_output = globals()[_io.io]
                if _io.worker in __hmworkerlist__:
                    _tar = (_io.worker, ("hivemap", _io.workerio))

                elif _io.workerio.find(".") > -1:  # dragonfly.block workers, never on hivemaphive
                    _tar2 = tuple(_io.workerio.split("."))
                    _tar = (_io.worker, _tar2)
                    del _tar2

                else:
                    _tar = getattr(locals()[_io.worker], _io.workerio)

                locals()[_io.io_id] = _antenna_output(_tar, mode=_io.mode, type_=_io.datatype)
                del _tar

                del _antenna_output, _io

        del _wdids

    del __hop_in_id_to_name__
    del __hop_out_id_to_name__

    return maphive


class HivemapTypeError(Exception):

    def __str__(self):
        ret = "\n" + str(self.args[0]) + "\n"
        ret += "".join(self.args[1]) + "\n"
        ret += "TypeError:" + str(self.args[2])
        return ret

    __repr__ = __str__


class HivemapValueError(Exception):

    def __str__(self):
        ret = "\n" + str(self.args[0]) + "\n"
        ret += "".join(self.args[1]) + "\n"
        ret += "ValueError:" + str(self.args[2])
        return ret

    __repr__ = __str__


def make_hivemap(hm, __subcontext__=None, *args, **kwargs):
    maphive = build_hivemap(hm)

    try:
        return maphive(*args, **kwargs).getinstance()

    except TypeError as e:
        raise  # ##TODO
        if __subcontext__ is None: raise
        import sys, traceback

        tb = sys.exc_info()[2]
        tbstack = traceback.extract_tb(tb)
        tblist = traceback.format_list(tbstack)
        raise HivemapTypeError(__subcontext__, tblist, e.args)

    except ValueError as e:
        raise  # ##TODO
        if __subcontext__ is None:
            raise

        import sys, traceback

        tb = sys.exc_info()[2]
        tbstack = traceback.extract_tb(tb)
        tblist = traceback.format_list(tbstack)
        raise HivemapValueError(__subcontext__, tblist, e.args)


class hivemapframe(spyderframe):
    SpyderMethod("make_bee", "Hivemap", make_hivemap)


class hivemaphive(spyderhive):
    SpyderMethod("make_bee", "Hivemap", make_hivemap)


class hivemapinithive(spyderinithive):
    SpyderMethod("make_bee", "Hivemap", make_hivemap)
