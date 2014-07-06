import sys, os


def register(currdir):
    from .worker import WorkerBuilder_module

    WorkerBuilder_module.support_simplified = True
    from . import HGui, PGui, HBlender, PBlender

    HGui.init(HBlender)
    PGui.init(PBlender)

    from .HBlender import BlendManager, NodeTree, HivemapBindPanel

    NodeTree.register()
    hiveguidir = os.path.split(__file__)[0]
    BlendManager.initialize(currdir, hiveguidir)
    BlendManager.blendmanager.register()
    HivemapBindPanel.register()


def unregister():
    from .HBlender import BlendManager, NodeTree, HivemapBindPanel

    BlendManager.unregister()
    NodeTree.unregister()
    HivemapBindPanel.unregister()