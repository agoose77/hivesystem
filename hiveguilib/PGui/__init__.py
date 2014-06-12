from __future__ import print_function, absolute_import


class PGui(object):
    def p(self):
        raise AttributeError("Abstract method PGui.p() must be re-implemented")


from .PWindow import PWindow
from .PWidgetWindow import PWidgetWindow
from .PWorkerCreator import PWorkerCreator
from .PDroneCreator import PDroneCreator


def init(pmodule):
    globals()["pmodule"] = pmodule
    globals()["PGenerator"] = pmodule.PGenerator
    from .PManager import PManager

    globals()["PManager"] = PManager
    globals()["PTree"] = pmodule.PTree
    from .PControllerGeneral import PControllerGeneral as PC

    class PControllerGeneral(PC):
        _PControllerGeneralClass = pmodule.PControllerGeneral

    globals()["PControllerGeneral"] = PControllerGeneral

    from .PControllerBlock import PControllerBlock as PCB

    class PControllerBlock(PCB):
        _PControllerBlockClass = pmodule.PControllerBlock

    globals()["PControllerBlock"] = PControllerBlock

    from .PSpyderhive import PSpyderhive as PS

    class PSpyderhive(PS):
        _PSpyderhiveClass = pmodule.PSpyderhive

    globals()["PSpyderhive"] = PSpyderhive

    from .AntennaFoldState import AntennaFoldState as AFS

    class AntennaFoldState(AFS):
        _AntennaFoldStateClass = pmodule.AntennaFoldState

    globals()["AntennaFoldState"] = AntennaFoldState
  
