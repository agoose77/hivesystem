from . import socket_base
from .socketmixins import *


class socket_single_optional(
    socket_base,
    socket_mixin_single,
    socket_mixin_optional,
):
    pass


class socket_single_required(
    socket_base,
    socket_mixin_single,
    socket_mixin_required,
):
    pass


class socket_multi_required(
    socket_base,
    socket_mixin_multi,
    socket_mixin_required,
):
    pass


class socket_container(
    socket_base,
    socket_mixin_multi,
    socket_mixin_optional,
):
    pass


class socket_supplier(socket_container):
    pass


class socket_flag(
    socket_base,
    socket_mixin_multi,
    socket_mixin_required
):
    def __init__(self):
        def nullfunc(arg):
            pass

        socket_base.__init__(self, nullfunc)
