import bpy
import logging

from . import BlendManager


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


@bpy.app.handlers.persistent
def game_pre(dummy):
    scene = bpy.context.scene

    for obj in scene.objects:
        if not obj.hive_nodetree:
            continue

        blend_manager = BlendManager.blendmanager
        try:
            nodetree_manager = blend_manager.get_nodetree_manager(obj.hive_nodetree)

        except KeyError:
            logging.warning("Couldn't find nodetree for {} called {}".format(obj.name, obj.hive_nodetree))
            continue

        textblock_name = blend_manager.get_textblock_name(nodetree_manager)

        hivemap_prop = create_property(obj, "hivemap")
        hivemap_prop.value = textblock_name
        hivemap_prop.show_debug = 1


@bpy.app.handlers.persistent
def game_post(dummy):
    scene = bpy.context.scene

    for obj in scene.objects:
        if not obj.hive_nodetree:
            continue

        try:
            remove_property(obj, "hivemap")

        except KeyError:
            continue


class HivemapSelectionPanel(bpy.types.Panel):
    bl_space_type = "LOGIC_EDITOR"
    bl_region_type = "UI"
    bl_label = "Hive Logic"
    COMPAT_ENGINES = {'BLENDER_GAME'}

    @classmethod
    def on_registered(cls):
        # Template list settings
        bpy.types.Object.hive_nodetree = bpy.props.StringProperty("", description="NodeTree to bind to")
        try:
            bpy.app.handlers.game_pre.append(game_pre)
            bpy.app.handlers.game_post.append(game_post)

        except AttributeError:
            pass


    @classmethod
    def on_unregistered(cls):
        try:
            bpy.app.handlers.game_pre.remove(game_pre)
            bpy.app.handlers.game_post.remove(game_post)

        except AttributeError:
            pass

    def draw(self, context):
        layout = self.layout
        ob = bpy.context.object
        layout.prop_search(ob, "hive_nodetree", bpy.data, "node_groups", text="NodeTree")


def register():
    bpy.utils.register_class(HivemapSelectionPanel)
    HivemapSelectionPanel.on_registered()


def unregister():
    bpy.utils.unregister_class(HivemapSelectionPanel)
    HivemapSelectionPanel.on_unregistered()
