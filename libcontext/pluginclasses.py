from . import plugin_base
from .pluginmixins import *


class plugin_single_required(
    plugin_base,
    plugin_mixin_single,
    plugin_mixin_required,
):
    pass


class plugin_single_optional(
    plugin_base,
    plugin_mixin_single,
    plugin_mixin_optional,
):
    pass


class plugin_multi_required(
    plugin_base,
    plugin_mixin_multi,
    plugin_mixin_required,
):
    pass


class plugin_supplier(
    plugin_base,
    plugin_mixin_multi,
    plugin_mixin_optional,
):
    pass


class plugin_flag(
    plugin_base,
    plugin_mixin_multi,
    plugin_mixin_optional,
):
    def __init__(self):
        plugin_base.__init__(self, None)

