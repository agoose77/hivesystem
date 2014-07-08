import bpy
import logging

from . import BlendManager
from .NodeTrees import HivemapNodeTree


def get_property(obj, name):
    return obj.game.properties[name]


def create_property(obj, name, type_="STRING"):
    bpy.context.scene.objects.active = obj
    bpy.ops.object.game_property_new(type=type_, name=name)
    return obj.game.properties[name]


def remove_property(obj, name):
    bpy.context.scene.objects.active = obj
    prop_index = obj.game.properties.find(name)
    if prop_index == -1:
        raise KeyError("Couldn't find property called {}".format(name))

    bpy.ops.object.game_property_remove(index=prop_index)


def get_or_create_property(obj, name, type_="STRING"):
    try:
        prop = get_property(obj, name)

    except KeyError:
        prop = create_property(obj, name, type_)

    return prop


def ui_hivemap_set(obj, context):
    nodetree_name = obj.hive_nodetree

    if not nodetree_name:
        try:
            remove_property(obj, "hivemap")
        finally:
            return

    blend_manager = BlendManager.blendmanager

    try:
        nodetree_manager = blend_manager.get_nodetree_manager(nodetree_name)

    except KeyError:
        logging.warning("Couldn't find nodetree for {} called {}".format(obj.name, nodetree_name))
        return

    textblock_name = blend_manager.get_textblock_name(nodetree_manager)

    hivemap_prop = get_or_create_property(obj, "hivemap")
    hivemap_prop.value = textblock_name
    hivemap_prop.show_debug = 1


_object = None

@bpy.app.handlers.persistent
def tree_switcher(dummy):
    scene = bpy.context.scene
    if scene is None:
        return

    if not scene.switch_to_bound_hive_tree:
        return

    active_object = bpy.context.scene.objects.active
    global _object

    if active_object == _object or active_object is None:
        return

    node_tree_name = active_object.hive_nodetree
    try:
        node_tree = bpy.data.node_groups[node_tree_name]
    except KeyError:
        return

    blend_manager = BlendManager.blendmanager

    try:
        nodetree_manager = blend_manager.get_nodetree_manager(node_tree.name)

    except KeyError:
        return

    for space in (sp for s in bpy.data.screens for a in s.areas for sp in a.spaces if sp.type == "NODE_EDITOR"):
        if space.tree_type != nodetree_manager.tree_bl_idname:
            continue

        space.node_tree = node_tree
        logging.info("Switched to {}".format(node_tree.name))
        break

    _object = active_object


class HivemapSelectionPanel(bpy.types.Panel):
    bl_space_type = "LOGIC_EDITOR"
    bl_region_type = "UI"
    bl_label = "Hive Logic"
    COMPAT_ENGINES = {'BLENDER_GAME'}

    @classmethod
    def on_registered(cls):
        # Template list settings
        bpy.types.Object.hive_nodetree = bpy.props.StringProperty("", description="NodeTree to bind to",
                                                                  update=ui_hivemap_set)

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        ob = bpy.context.object

        layout.prop_search(ob, "hive_nodetree", bpy.data, "node_groups", text="NodeTree")


def register():
    bpy.utils.register_class(HivemapSelectionPanel)
    HivemapSelectionPanel.on_registered()
    bpy.app.handlers.scene_update_post.append(tree_switcher)


def unregister():
    bpy.utils.unregister_class(HivemapSelectionPanel)
    HivemapSelectionPanel.on_unregistered()
    bpy.app.handlers.scene_update_post.remove(tree_switcher)
