from __future__ import print_function, absolute_import
import sys, os

import spyder
from . import HGui, PGui, HQt, PQt

PQt.PControllerGeneral.label = "Segment"
HGui.init(HQt)
PGui.init(PQt)
from . import WorkermapManager, Clipboard
from .PGui import PWindow, PWidgetWindow, PManager, PWorkerCreator, PControllerGeneral
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
    pwc = PWorkerCreator(mainWin, clipboard, "segments")
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
    currdir = os.path.split(__file__)[0]
    seg = [
        "segments.antenna",
        "segments.output",
        "segments.variable",
        "segments.buffer",
        "segments.transistor",
        "segments.modifier",
        "segments.weaver",
        "segments.unweaver",
        "segments.operator",
        "segments.test",
        "segments.custom_code",
    ]
    wf = wfc(seg, [currdir])
    workermanager._workerfinder_global = wf
    workermanager._update_typelist()
    workermanager.build_workers(local=False)

    workermapmanager = WorkermapManager(
        mainWin, workermanager, workerinstancemanager, HGui.FileDialog
    )
    clipboard.set_mapmanager(workermapmanager)

    if len(argv) > 1:
        workermapfile = argv[1]
        workermapmanager.load(workermapfile)
        workermapmanager._lastsave = workermapfile

    if readmetxt is not None:
        dialog = QtGui.QDialog()
        dialog.setMinimumSize(600, 800)
        dialog.setModal(False)
        pte = QtGui.QPlainTextEdit(readmetxt, dialog)
        pte.setMinimumSize(600, 800)
        dialog.show()

    app.h().mainloop()

