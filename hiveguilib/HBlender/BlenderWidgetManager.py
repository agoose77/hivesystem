import bpy


class WidgetCounter:
    def increment(self, attr):
        if not hasattr(self, attr): setattr(self, attr, 0)
        v = getattr(self, attr) + 1
        setattr(self, attr, v)
        return v


buttoncounter = 0
_widgetcounters = {}


def _generate_identifier(widgetcounter, proptypename):
    return "hive_blender_widget_" + proptypename + "_" + str(widgetcounter.increment(proptypename))


def define_widget_button(callback, **kwargs):
    global buttoncounter
    buttoncounter += 1
    otname = "OT_NODE_hive_blender_button_%d" % buttoncounter
    identifier = "node.hive_blender_button_%d" % buttoncounter

    def callback0(dummy, dummy2):
        callback()
        return {'FINISHED'}

    otd = dict(
        bl_idname=identifier,
        bl_label=identifier,
        bl_options={'INTERNAL'},
        execute=callback0
    )
    ot = type(otname, (bpy.types.Operator,), otd)
    bpy.utils.register_class(ot)
    return identifier


def define_widget(proptype, proptypename, getter, setter, **kwargs):
    sceneid = bpy.context.scene.as_pointer()
    if sceneid not in _widgetcounters: _widgetcounters[sceneid] = WidgetCounter()
    widgetcounter = _widgetcounters[sceneid]
    identifier = _generate_identifier(widgetcounter, proptypename)

    def getter0(dummy): return getter()

    def setter0(dummy, v): return setter(v)

    prop = proptype(get=getter0, set=setter0, **kwargs)
    setattr(bpy.types.Scene, identifier, prop)
    return identifier
