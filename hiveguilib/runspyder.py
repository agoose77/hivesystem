from __future__ import print_function, absolute_import
import sys, os

import spyder
from . import HGui, PGui, HQt, PQt

PQt.PControllerGeneral.label = "Bee"
HGui.init(HQt)
PGui.init(PQt)
from . import SpydermapManager, Clipboard
from .PGui import PWindow, PWidgetWindow, PManager, PWorkerCreator, \
    PControllerGeneral, PSpyderhive
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
    pwins = {}
    pwins["general"] = PWindow(mainWin, "props-general", controller_general)
    pwins["params"] = PWidgetWindow(mainWin, "props-params")
    pwins["metaparams"] = PWidgetWindow(mainWin, "props-metaparams")
    pmanager = PManager(pwins)
    pwc = PWorkerCreator(mainWin, clipboard, "bees")
    psh = PSpyderhive(mainWin, "spyderhive")
    mainWin.show()

    currdir = os.path.abspath(os.path.dirname(argv[0]))
    workerbuilder = WorkerBuilder()
    workerinstancemanager = WorkerInstanceManager(canvas)
    controller_general.set_workerinstancemanager(workerinstancemanager)
    workermanager = WorkerManager(
        workerbuilder, workerinstancemanager, pmanager, pwc,
        with_blocks=False
    )
    controller_general.set_workermanager(workermanager)
    clipboard.set_workermanager(workermanager)

    # Implement tab completion for widgets describing data types
    from .PQt import TypeCompleter

    typecompleter = TypeCompleter()
    workermanager.add_typelist_listener(typecompleter.set_typelist)
    pmanager.modifiers.append(typecompleter.widgetmodifier)

    wfc = workermanager._workerfinderclass
    hiveguidir = os.path.split(__file__)[0]

    workermanager.find_global_worFkers(currdir, hiveguidir, remove=False)  #just to find spyderhives

    spydermapmanager = SpydermapManager(
        mainWin,
        workermanager, workerinstancemanager, psh,
        HGui.FileDialog
    )
    clipboard.set_mapmanager(spydermapmanager)
    spydermapmanager.store_spyderhive_global_candidates()

    spyderbees = [
        "spyderbees.*",
    ]
    wf = wfc(spyderbees, [hiveguidir])
    workermanager._workerfinder_global = wf

    workermanager.build_workers(local=False)

    if len(argv) > 1:
        spydermapfile = argv[1]
        spydermapmanager.load(spydermapfile)
        spydermapmanager._lastsave = spydermapfile
    else:
        spydermapmanager.find_spyderhive_candidates()

    if readmetxt is not None:
        dialog = QtGui.QDialog()
        dialog.setMinimumSize(600, 800)
        dialog.setModal(False)
        pte = QtGui.QPlainTextEdit(readmetxt, dialog)
        pte.setMinimumSize(600, 800)
        dialog.show()

    app.h().mainloop()

