import libcontext
from bee.bind import *
from bee.staticbind import staticbind_baseclass


class staticbind(staticbind_baseclass):
    bind_doexit = bindparameter(True)
    binder("bind_doexit", False, None)
    binder("bind_doexit", True, pluginbridge("doexit"))
