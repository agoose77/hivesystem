from . import types
from .hivemodule import BeeHelper
from .types import get_parameterclass


class Parameter(object):

    def __init__(self, typename, gui_defaultvalue="no-defaultvalue"):
        self.typename = typename
        self.parameterclass = get_parameterclass(self.typename)
        self.gui_defaultvalue = gui_defaultvalue