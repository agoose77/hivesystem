from __future__ import print_function, absolute_import
import sys, os

import spyder
from . import HGui, PGui, HQt, PQt

HGui.init(HQt)
PGui.init(PQt)
from . import HivemapManager, Clipboard
from .worker import WorkerManager, WorkerBuilder, WorkerInstanceManager


def run(readmetxt=None):
    argv = [a for a in sys.argv if not a.startswith("--")]
    app = HGui.Application(argv)
    from .HQt.anyQt import QtGui

    mainWin = HGui.MainWindow()
    clipboard = Clipboard()
    statusbar = HGui.StatusBar(mainWin)
    canvas = HGui.NodeCanvas(mainWin, clipboard, statusbar)
    controller_general = PGui.PControllerGeneral()
    controller_block = PGui.PControllerBlock()
    pwins = {}
    pwins["general"] = PGui.PWindow(mainWin, "props-general", controller_general)
    pwins["params"] = PGui.PWidgetWindow(mainWin, "props-params")
    pwins["metaparams"] = PGui.PWidgetWindow(mainWin, "props-metaparams")
    pwins["block"] = PGui.PWindow(mainWin, "props-block", controller_block)
    pmanager = PGui.PManager(pwins)
    pwc = PGui.PWorkerCreator(mainWin, clipboard)
    pdc = PGui.PDroneCreator(mainWin, clipboard)
    mainWin.show()

    currdir = os.path.abspath(os.path.dirname(argv[0]))
    workerbuilder = WorkerBuilder()
    workerinstancemanager = WorkerInstanceManager(canvas)
    controller_general.set_workerinstancemanager(workerinstancemanager)
    controller_block.set_workerinstancemanager(workerinstancemanager)
    workermanager = WorkerManager(
        workerbuilder, workerinstancemanager, pmanager, pwc, pdc
    )
    antennafoldstate = PGui.AntennaFoldState(canvas, workermanager)
    workermanager.set_antennafoldstate(antennafoldstate)
    controller_general.set_workermanager(workermanager)
    controller_block.set_workermanager(workermanager)
    clipboard.set_workermanager(workermanager)
    canvas.set_workermanager(workermanager)

    # Implement tab completion for widgets describing data types
    from .PQt import TypeCompleter

    typecompleter = TypeCompleter()
    workermanager.add_typelist_listener(typecompleter.set_typelist)
    pmanager.modifiers.append(typecompleter.widgetmodifier)

    hiveguidir = os.path.split(__file__)[0]
    workermanager.find_global_workers(currdir, hiveguidir)
    workermanager.build_workers(local=False)

    hivemapmanager = HivemapManager(
        mainWin, workermanager, workerinstancemanager, HGui.FileDialog
    )
    clipboard.set_mapmanager(hivemapmanager)

    if len(argv) > 1:
        hivemapfile = argv[1]
        hivemapmanager.load(hivemapfile)
        hivemapmanager._lastsave = hivemapfile

    if readmetxt is not None:
        dialog = QtGui.QDialog()
        dialog.setMinimumSize(600, 800)
        dialog.setModal(False)
        pte = QtGui.QPlainTextEdit(readmetxt, dialog)
        pte.setMinimumSize(600, 800)
        dialog.show()

    app.h().mainloop()

