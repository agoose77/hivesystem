import libcontext
from bee.bind import *
from bee.staticbind import staticbind_baseclass


class hiveloader(binderdrone):

    def bind(self, bindworker, hivename):
        bindworker.hive = self.get_hive(hivename)

    def set_get_hive(self, get_hive):
        self.get_hive = get_hive

    def place(self):
        s = libcontext.socketclasses.socket_single_required(self.set_get_hive)
        libcontext.socket("get_hive", s)


class bind(bind_baseclass):
    hivename = bindantenna("id")
    prebinder(hiveloader(), "hivename")
    bind_doexit = bindparameter(True)
    binder("bind_doexit", False, None)
    binder("bind_doexit", True, pluginbridge("doexit"))
  
