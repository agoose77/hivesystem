from __future__ import print_function, absolute_import
from bee.types import boolparser, spyderparser

import os
import spyder, Spyder


class SpydermapManager(object):

    def __init__(self, mainwin, workermanager, workerinstancemanager, pspyderhive, file_dialog):
        self._mainwin = mainwin
        self._wim = workerinstancemanager
        self._workermanager = workermanager
        self._pspyderhive = pspyderhive
        pspyderhive.set_spydermapmanager(self)
        self._file_dialog = file_dialog

        self._lastsave = None
        self._spyderhive = None

        win = self._mainwin.h()
        win.add_menu("&File")
        win.add_menu_action(
            "&File",
            "&New",
            self.clear,
            shortcut="Ctrl+N",
            statustip="Close the current Spydermap file and open a new one",
        )
        win.add_menu_action(
            "&File",
            "&Open",
            self.menu_load,
            shortcut="Ctrl+O",
            statustip="Open a Spydermap file",
        )
        win.add_menu_action(
            "&File",
            "&Save",
            self.menu_save,
            shortcut="Ctrl+S",
            statustip="Save the current Spydermap file",
        )
        win.add_menu_action(
            "&File",
            "Save as",
            self.menu_save_as,
            statustip="Save the current Spydermap file in the desired location",
        )
        win.add_menu_action(
            "&File",
            "&Quit",
            win.close,
            shortcut="Ctrl+Q",
            statustip="Quits the editor",
        )

    def _load(self, spydermap, soft_load=False, pre_load=None):
        self.set_spyderhive(spydermap.spyderhive)
        coordinates = spydermap.coordinates
        if coordinates is None:
            coordinates = [(0, 0)] * len(spydermap.names)
        else:
            coordinates = [(c.x, c.y) for c in coordinates]

        paramcoordinates = spydermap.paramcoordinates
        if paramcoordinates is None:
            paramcoordinates = [(0, 0)] * len(spydermap.parameters)
        else:
            paramcoordinates = [(c.x, c.y) for c in paramcoordinates]

        for name, data, c in zip(spydermap.names, spydermap.objectdata, coordinates):
            x, y = c
            self._workermanager.instantiate(
                name, "spyderbees.attribute", x, y,
                {"spydertype": data.typename()},
                {"val": data},
            )

        for name, c in zip(spydermap.parameters, paramcoordinates):
            x, y = c
            self._workermanager.instantiate(
                name, "spyderbees.parameter", x, y
            )

        for wasp in spydermap.wasps:
            name = wasp.wasp_id
            x, y = wasp.position.x, wasp.position.y
            data = spyderparser(wasp.spydertypename, wasp.spydervalue)
            self._workermanager.instantiate(
                name, "spyderbees.wasp", x, y,
                {"spydertype": wasp.spydertypename},
                {
                    "val": data,
                    "target": wasp.target,
                    "targetparam": wasp.targetparam,
                },
            )


    def find_spyderhive_candidates(self):
        s = self._workermanager.get_spyderhives()
        candidates = self._spyderhive_global_candidates + list(s.keys())
        stds = (
            "bee.spyderhive.spyderframe",
            "bee.spyderhive.spyderhive",
            "bee.spyderhive.spyderdicthive",
            "bee.combohive",
        )
        for std in stds:
            if std not in candidates:
                candidates.insert(0, std)
        self._pspyderhive.set_spyderhive_candidates(candidates)
        return candidates

    def store_spyderhive_global_candidates(self):
        self._spyderhive_global_candidates = []
        self._spyderhive_global_candidates = self.find_spyderhive_candidates()

    def gui_sets_spyderhive(self, spyderhive):
        self._spyderhive = spyderhive
        return True

    def set_spyderhive(self, spyderhive):
        self._spyderhive = spyderhive
        self._pspyderhive.update_spyderhive(spyderhive)

    def load(self, spydermapfile):
        self.clear()

        workermanager = self._workermanager
        localdir = os.path.split(spydermapfile)[0]
        workermanager.find_local_workers(localdir)  # just to find spyderhives
        self.find_spyderhive_candidates()

        spydermap = Spyder.Spydermap.fromfile(spydermapfile)
        self._load(spydermap)

    def save(self, spydermapfilename, filesaver=None):
        # Default to all worker ids
        worker_ids = self._workermanager.workerids()
        spydermap = self._save(worker_ids)

        # Save to file
        spydermap_string = str(spydermap)

        if filesaver:
            filesaver(spydermapfilename, spydermap_string)

        else:
            spydermap.tofile(spydermapfilename)

        self._lastsave = spydermapfilename

    def _save(self, worker_ids):
        workermanager = self._workermanager

        spydernames = Spyder.StringArray()
        spyderobjectdata = Spyder.ObjectList()
        spyderparameters = Spyder.StringArray()
        wasps = Spyder.SpydermapWaspArray()
        coordinates = Spyder.Coordinate2DArray()
        paramcoordinates = Spyder.Coordinate2DArray()

        for workerid in sorted(worker_ids):
            node, mapping = self._wim.get_node(workerid)
            if node.empty:
                continue

            workertype, params, metaparams = workermanager.get_parameters(workerid)

            if params is None: params = {}
            if metaparams is None: metaparams = {}
            if workertype == "spyderbees.attribute":
                spydertype = metaparams.get("spydertype", None)
                if spydertype is None:
                    print("Warning: attribute '%s' has no spydertype, skipped!" % workerid)
                    continue
                spydervalue = params.get("val", None)
                if spydervalue is None:
                    print("Warning: attribute '%s' (%s) has no value, skipped!" % (workerid, spydertype))
                    continue
                spydernames.append(workerid)
                spyderobjectdata.append(spydervalue)
                coordinates.append(Spyder.Coordinate2D(node.position))
            elif workertype == "spyderbees.parameter":
                spyderparameters.append(workerid)
                paramcoordinates.append(Spyder.Coordinate2D(node.position))
            elif workertype == "spyderbees.wasp":
                spydertype = metaparams.get("spydertype", None)
                if spydertype is None:
                    print("Warning: wasp '%s' has no spydertype, skipped!" % workerid)
                    continue
                spydervalue = params.get("val", None)
                if spydervalue is None:
                    print("Warning: wasp '%s' (%s) has no value, skipped!" % (workerid, spydertype))
                    continue
                wasp = Spyder.SpydermapWasp(
                    workerid,
                    spydertype,
                    str(spydervalue),
                    params.get("target", ""),
                    params.get("targetparam", ""),
                    node.position,
                )
                wasps.append(wasp)
            else:
                raise Exception(workertype)

        spydermap = Spyder.Spydermap.empty()
        spyderhive = self._spyderhive
        if spyderhive is None:
            spyderhive = ""

        spydermap.spyderhive = spyderhive
        spydermap.names = spydernames
        spydermap.objectdata = spyderobjectdata
        spydermap.parameters = spyderparameters
        spydermap.coordinates = coordinates
        spydermap.paramcoordinates = paramcoordinates
        spydermap.wasps = wasps
        return spydermap

    def menu_save_as(self):
        spydermapfile = self._file_dialog("save")
        self.save(spydermapfile)

    def menu_save(self):
        if self._lastsave is None:
            return self.menu_save_as()
        self.save(self._lastsave)

    def menu_refresh(self):
        if self._lastsave is None: return
        self.save(self._lastsave)
        self.load(self._lastsave)

    def menu_load(self):
        spydermapfile = self._file_dialog("open")
        self.load(spydermapfile)
        self._lastsave = spydermapfile

    def clear(self):
        self._workermanager.clear_workers()
