import sys, os


def register(currdir):
    from .worker import WorkerBuilder_module

    WorkerBuilder_module.support_simplified = True
    from . import HGui, PGui, HBlender, PBlender

    HGui.init(HBlender)
    PGui.init(PBlender)

    from .HBlender import BlendManager, NodeTrees, Menus, Operators, HivemapBindPanel

    NodeTrees.register()
    Operators.register()
    Menus.register()

    hiveguidir = os.path.split(__file__)[0]
    BlendManager.initialize(currdir, hiveguidir)
    BlendManager.blendmanager.register()
    HivemapBindPanel.register()


def unregister():
    from .HBlender import BlendManager, NodeTrees, Menus, Operators, HivemapBindPanel

    BlendManager.blendmanager.unregister()
    NodeTrees.unregister()
    Operators.unregister()
    Menus.unregister()
    HivemapBindPanel.unregister()