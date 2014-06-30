from __future__ import print_function, absolute_import

import os
import spyder, Spyder

from .workergen import workergen


class WorkermapManager(object):
    def __init__(self, mainwin, workermanager, workerinstancemanager, file_dialog):
        self._mainwin = mainwin
        self._wim = workerinstancemanager
        self._workermanager = workermanager
        self._file_dialog = file_dialog

        self._lastsave = None
        self._dialogs = []  # TODO: get rid of closed dialogs..

        win = self._mainwin.h()
        win.add_menu("&File")
        win.add_menu_action(
            "&File",
            "&New",
            self.clear,
            shortcut="Ctrl+N",
            statustip="Close the current Workermap file and open a new one",
        )
        win.add_menu_action(
            "&File",
            "&Open",
            self.menu_load,
            shortcut="Ctrl+O",
            statustip="Open a Workermap file",
        )
        win.add_menu_action(
            "&File",
            "&Save",
            self.menu_save,
            shortcut="Ctrl+S",
            statustip="Save the current Workermap file",
        )
        win.add_menu_action(
            "&File",
            "Save as",
            self.menu_save_as,
            statustip="Save the current Workermap file in the desired location",
        )
        win.add_menu_action(
            "&File",
            "&Quit",
            win.close,
            shortcut="Ctrl+Q",
            statustip="Quits the editor",
        )
        win.add_menu("&Generate")
        win.add_menu_action(
            "&Generate",
            "&Generate code",
            self.generate,
            shortcut="Ctrl+G",
            statustip="Generate Python code",
        )

    def _load(self, workermap, soft_load=False, pre_load=None):
        segment_id_mapping = {}

        for seg in workermap.segments:
            x, y = seg.position.x, seg.position.y
            metaparamvalues = None
            if seg.metaparameters is not None:
                metaparamvalues = {}
                for param in seg.metaparameters:
                    metaparamvalues[param.pname] = param.pvalue
            paramvalues = None
            if seg.parameters is not None:
                paramvalues = {}
                for param in seg.parameters:
                    paramvalues[param.pname] = param.pvalue


            worker_ids = self._workermanager.workerids()

            # If an ID clash occurred
            segment_id = seg.segid

            if segment_id in worker_ids and soft_load:
                old_segment_id = segment_id
                segment_id = self._workermanager.get_new_workerid(segment_id)
                segment_id_mapping[old_segment_id] = segment_id

                if callable(pre_load):
                    pre_load(old_segment_id, segment_id)

            else:
                # The new ID and the previous ID are the same
                if callable(pre_load):
                    pre_load(segment_id, segment_id)

            try:
                self._workermanager.instantiate(
                    segment_id, seg.segtype, x, y, metaparamvalues, paramvalues
                )
                if seg.profile != "default":
                    self._wim.morph_worker(segment_id, seg.profile)
            except KeyError:
                print("Unknown segment:", seg.segtype, segment_id.split(".")[-1])
                continue

        for connection in workermap.connections:
            connection_id = self._workermanager.get_new_connection_id("con")
            interpoints = [(ip.x, ip.y) for ip in connection.interpoints]

            # Account for renamed segments
            start_id = segment_id_mapping.get(connection.start.segid, connection.start.segid)
            end_id = segment_id_mapping.get(connection.end.segid, connection.end.segid)

            self._wim.add_connection(connection_id, (start_id, connection.start.io),
                                     (end_id, connection.end.io), interpoints)

    def load(self, workermapfile):
        self.clear()

        # Just to find Spyder models...
        workermanager = self._workermanager
        localdir = os.path.split(workermapfile)[0]
        workermanager.find_local_workers(localdir)
        self._workerfinder_local = None

        workermap = Spyder.Workermap.fromfile(workermapfile)
        self._load(workermap)

    def _save(self, worker_ids):
        workermanager = self._workermanager
        segments, connections = [], []
        for segid in sorted(worker_ids):
            node, mapping = self._wim.get_node(segid)
            if node.empty: continue
            segtype, params, metaparams = workermanager.get_parameters(segid)
            if params is not None: params = params.items()
            if metaparams is not None: metaparams = metaparams.items()
            profile = self._wim.get_workerinstance(segid).curr_profile

            seg = Spyder.WorkerSegment(
                segid,
                segtype,
                node.position,
                parameters=params,
                metaparameters=metaparams,
                profile=profile,
            )
            segments.append(seg)

        for connection in self._wim.get_connections():

            # Only save wanted connections
            if not (connection.start_node in worker_ids and connection.end_node in worker_ids):
                continue

            start_node, start_mapping = self._wim.get_node(connection.start_node)
            if start_mapping is None:
                raise KeyError(connection.start_node)
            end_node, end_mapping = self._wim.get_node(connection.end_node)
            if end_mapping is None:
                raise KeyError(connection.end_node)

            start_attribute = start_mapping._outmapr[connection.start_attribute]
            end_attribute = end_mapping._inmapr[connection.end_attribute]
            con = Spyder.WorkerSegmentConnection(
                (connection.start_node, start_attribute),
                (connection.end_node, end_attribute),
                connection.interpoints
            )
            connections.append(con)
        workermap = Spyder.Workermap(segments, connections)
        return workermap

    def save(self, workermapfile, filesaver=None):
        workermap = self._save(self._workermanager.workerids())
        if filesaver:
            filesaver(workermapfile, str(workermap))
        else:
            workermap.tofile(workermapfile)
        self._lastsave = workermapfile
        return workermap

    def menu_save_as(self):
        workermapfile = self._file_dialog("save")
        self.save(workermapfile)

    def menu_save(self):
        if self._lastsave is None:
            return self.menu_save_as()
        self.save(self._lastsave)

    def menu_load(self):
        workermapfile = self._file_dialog("open")
        self.load(workermapfile)
        self._lastsave = workermapfile

    def clear(self):
        self._workermanager.clear_workers()

    def generate(self):
        workermap = self._save()
        name = "myworker"
        if self._lastsave is not None:
            f = os.path.split(self._lastsave)[1]
            name = f.split(".")[-2:][0]
        code = None
        try:
            code = workergen(name, workermap)
            from .HQt.anyQt import QtGui
            from .PQt.pythoncode import highlight, set_css

            dialog = QtGui.QDialog()
            dialog.setMinimumSize(600, 800)
            dialog.setModal(False)
            dialog.setWindowTitle("Generated Python code for '%s'" % name)
            textedit = QtGui.QTextEdit(parent=dialog)
            textedit.setMinimumSize(600, 800)
            dialog.show()
            textedit.append(code)
            self._dialogs.append(dialog)
            set_css(textedit)
            highlight(textedit)
        except:
            import traceback

            traceback.print_exc()
            if code is not None: print(code)
    
