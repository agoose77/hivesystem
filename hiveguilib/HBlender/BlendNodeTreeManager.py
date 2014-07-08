import bpy, os, logging
from .. import HGui, PGui
from .. import HivemapManager, WorkermapManager, SpydermapManager, Clipboard
from ..worker import WorkerManager, WorkerBuilder, WorkerInstanceManager
from . import BlenderTextWidget


class BlendNodeTreeManager:

    tree_bl_idname = None

    def __init__(self, parent, name):
        self.parent = parent
        self.name = name

    def get_nodetree(self):
        return bpy.data.node_groups[self.name]


class HiveMapNodeTreeManager(BlendNodeTreeManager):

    tree_bl_idname = "Hivemap"

    def __init__(self, parent, name):
        super(). __init__(parent, name)

        self.mainWin = HGui.MainWindow()
        self.statusbar = HGui.StatusBar(self.mainWin)
        self.clipboard = Clipboard()
        self.canvas = HGui.NodeCanvas(self.mainWin, self.clipboard, self.statusbar)
        self.canvas.observers_selection.append(BlenderTextWidget.manager.select)
        self.canvas.h().set_blendnodetreemanager(self)
        self.controller_general = PGui.PControllerGeneral()
        self.controller_block = PGui.PControllerBlock()
        self.workerbuilder = WorkerBuilder()
        self.workerinstancemanager = WorkerInstanceManager(self.canvas)
        try:
            currlevel = int(bpy.context.scene.hive_level)
            if currlevel == 1:
                self.workerinstancemanager.default_profile = "simplified"
        except:
            pass

        self.controller_general.set_workerinstancemanager(self.workerinstancemanager)
        self.controller_block.set_workerinstancemanager(self.workerinstancemanager)
        self.pwins = {}

        self.pwins["general"] = PGui.PWindow(self.mainWin, "props-general", self.controller_general)
        self.pwins["params"] = PGui.PWidgetWindow(self.mainWin, "props-params")
        self.pwins["metaparams"] = PGui.PWidgetWindow(self.mainWin, "props-metaparams")
        self.pwins["block"] = PGui.PWindow(self.mainWin, "props-block", self.controller_block)
        self.pmanager = PGui.PManager(self.pwins)
        self.pwc = PGui.PWorkerCreator(self.mainWin, self.clipboard)
        self.pdc = PGui.PDroneCreator(self.mainWin, self.clipboard)

        # In Qt, dragged widgets generate their own events;
        #In Blender,
        # 1. we have only a single shared panel
        # 2. drag/drop events don't exist, we have to define a new operator for every added NodeItem
        #Hence, the NodeItem manager
        self.pwc._tree.set_nodeitemmanager(self.parent.nodeitemmanager)
        self.pwc._tree.set_nodetreename(self.name)
        self.pdc._tree.set_nodeitemmanager(self.parent.nodeitemmanager)
        self.pdc._tree.set_nodetreename(self.name)

        self.workermanager = WorkerManager(
            self.workerbuilder, self.workerinstancemanager, self.pmanager, self.pwc, self.pdc
        )
        self.controller_general.set_workermanager(self.workermanager)
        self.controller_block.set_workermanager(self.workermanager)
        self.clipboard.set_workermanager(self.workermanager)
        self.canvas.set_workermanager(self.workermanager)

        self.antennafoldstate = PGui.AntennaFoldState(self.canvas, self.workermanager)
        self.workermanager.set_antennafoldstate(self.antennafoldstate)

        self.workermanager._workerfinder_global = self.parent._workerfinder_global_hivemap
        #TODO: update typelist??
        self.workermanager.build_workers(local=False)

        self.workermanager._workerfinder_local = self.parent._workerfinder_local_hivemap
        if self.workermanager._workerfinder_local:
            #TODO: update typelist??
            self.workermanager.build_workers(local=True)

        self.hivemapmanager = HivemapManager(
            self.mainWin, self.workermanager, self.workerinstancemanager, HGui.FileDialog
        )
        self.clipboard.set_mapmanager(self.hivemapmanager)


class WorkerMapNodeTreeManager(BlendNodeTreeManager):

    tree_bl_idname = "Workermap"

    def __init__(self, parent, name):
        super(). __init__(parent, name)

        self.mainWin = HGui.MainWindow()
        self.statusbar = HGui.StatusBar(self.mainWin)
        self.clipboard = Clipboard()
        self.canvas = HGui.NodeCanvas(self.mainWin, self.clipboard, self.statusbar)
        self.canvas.observers_selection.append(BlenderTextWidget.manager.select)
        self.canvas.h().set_blendnodetreemanager(self)
        self.controller_general = PGui.PControllerGeneral()
        self.workerbuilder = WorkerBuilder()
        self.workerinstancemanager = WorkerInstanceManager(self.canvas)
        self.controller_general.set_workerinstancemanager(self.workerinstancemanager)
        self.pwins = {}
        self.pwins["general"] = PGui.PWindow(self.mainWin, "props-general", self.controller_general)
        self.pwins["params"] = PGui.PWidgetWindow(self.mainWin, "props-params")
        self.pwins["metaparams"] = PGui.PWidgetWindow(self.mainWin, "props-metaparams")
        self.pmanager = PGui.PManager(self.pwins)
        self.pwc = PGui.PWorkerCreator(self.mainWin, self.clipboard)

        # In Qt, dragged widgets generate their own events;
        #In Blender,
        # 1. we have only a single shared panel
        # 2. drag/drop events don't exist, we have to define a new operator for every added NodeItem
        #Hence, the NodeItem manager
        self.pwc._tree.set_nodeitemmanager(self.parent.nodeitemmanager)
        self.pwc._tree.set_nodetreename(self.name)

        self.workermanager = WorkerManager(self.workerbuilder, self.workerinstancemanager, self.pmanager, self.pwc,
                                           with_blocks=False)
        self.controller_general.set_workermanager(self.workermanager)
        self.clipboard.set_workermanager(self.workermanager)

        self.workermanager._workerfinder_global = self.parent._workerfinder_global_workermap
        #TODO: update typelist??
        self.workermanager.build_workers(local=False)

        self.workermapmanager = WorkermapManager(
            self.mainWin, self.workermanager, self.workerinstancemanager, HGui.FileDialog
        )
        self.clipboard.set_mapmanager(self.workermapmanager)


class SpyderMapNodeTreeManager(BlendNodeTreeManager):

    tree_bl_idname = "Spydermap"

    def __init__(self, parent, name):
        super(). __init__(parent, name)

        self.mainWin = HGui.MainWindow()
        self.mainWin.h().nodetreemanager = self
        self.statusbar = HGui.StatusBar(self.mainWin)
        self.clipboard = Clipboard()
        self.canvas = HGui.NodeCanvas(self.mainWin, self.clipboard, self.statusbar)
        self.canvas.observers_selection.append(BlenderTextWidget.manager.select)
        self.canvas.h().set_blendnodetreemanager(self)
        self.controller_general = PGui.PControllerGeneral()
        self.workerbuilder = WorkerBuilder()
        self.workerinstancemanager = WorkerInstanceManager(self.canvas)
        self.controller_general.set_workerinstancemanager(self.workerinstancemanager)
        self.pwins = {}
        self.pwins["general"] = PGui.PWindow(self.mainWin, "props-general", self.controller_general)
        self.pwins["params"] = PGui.PWidgetWindow(self.mainWin, "props-params")
        self.pwins["metaparams"] = PGui.PWidgetWindow(self.mainWin, "props-metaparams")
        self.pmanager = PGui.PManager(self.pwins)
        self.pwc = PGui.PWorkerCreator(self.mainWin, self.clipboard)
        self.psh = PGui.PSpyderhive(self.mainWin, "spyderhive")

        # In Qt, dragged widgets generate their own events;
        #In Blender,
        # 1. we have only a single shared panel
        # 2. drag/drop events don't exist, we have to define a new operator for every added NodeItem
        #Hence, the NodeItem manager
        self.pwc._tree.set_nodeitemmanager(self.parent.nodeitemmanager)
        self.pwc._tree.set_nodetreename(self.name)

        self.workermanager = WorkerManager(self.workerbuilder, self.workerinstancemanager, self.pmanager, self.pwc,
                                           with_blocks=False)
        self.controller_general.set_workermanager(self.workermanager)
        self.clipboard.set_workermanager(self.workermanager)

        self.workermanager._workerfinder_global = self.parent._workerfinder_global_spydermap
        self.workermanager._workerfinder_local = self.parent._workerfinder_local_hivemap
        self.spydermapmanager = SpydermapManager(self.mainWin, self.workermanager, self.workerinstancemanager, self.psh,
                                                 HGui.FileDialog)
        self.clipboard.set_mapmanager(self.spydermapmanager)
        self.spydermapmanager._spyderhive_global_candidates = list(self.parent._workerfinder_global_spyderhives)
        self.spydermapmanager.find_spyderhive_candidates()
        self.workermanager.build_workers(local=False)
