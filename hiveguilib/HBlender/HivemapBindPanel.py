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
        logging.info("Switched to {} {}".format(node_tree_name, node_tree))


    _object = active_object


class HivemapSelectionPanel(bpy.types.Panel):
    bl_label = "Hive Logic"
    bl_idname = "OBJECT_PT_layout"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    COMPAT_ENGINES = {'BLENDER_GAME'}

    @classmethod
    def on_registered(cls):
        # Template list settings
        bpy.types.Object.hive_nodetree = bpy.props.StringProperty("", description="NodeTree to bind to",
                                                                  update=ui_hivemap_set)

        BlendManager.blendmanager.on_renamed.append(cls.on_renamed)
        BlendManager.blendmanager.on_removed.append(cls.on_removed)

    @classmethod
    def on_unregistered(cls):
        BlendManager.blendmanager.on_renamed.remove(cls.on_renamed)
        BlendManager.blendmanager.on_removed.remove(cls.on_removed)


    @classmethod
    def poll(cls, context):
        return context.object is not None

    @classmethod
    def on_renamed(cls, old_name, new_name):
        for obj in bpy.context.scene.objects:
            if obj.hive_nodetree != old_name:
                continue

            obj.hive_nodetree = new_name

    @classmethod
    def on_removed(cls, name):
        for obj in bpy.context.scene.objects:
            if obj.hive_nodetree != name:
                continue


            obj.hive_nodetree = ""

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        ob = context.active_object
        game = ob.game

        row = layout.row()
        row.label("Bound NodeTree")

        row = layout.row()
        row.prop_search(ob, "hive_nodetree", bpy.data, "node_groups", text="")

        row = layout.row()
        row.label("Properties")

        box = layout.box()
        is_font = (ob.type == 'FONT')

        if is_font:
            prop_index = game.properties.find("Text")
            if prop_index != -1:
                box.operator("object.game_property_remove", text="Remove Text Game Property", icon='X').index = prop_index
                row = box.row()
                sub = row.row()
                sub.enabled = 0
                prop = game.properties[prop_index]
                sub.prop(prop, "name", text="")
                row.prop(prop, "type", text="")
                # get the property from the body, not the game property
                # note, don't do this - it's too slow and body can potentially be a really long string.
                #~ row.prop(ob.data, "body", text="")
                row.label("See Text Object")
            else:
                props = box.operator("object.game_property_new", text="Add Text Game Property", icon='ZOOMIN')
                props.name = 'Text'
                props.type = 'STRING'

        props = box.operator("object.game_property_new", text="Add Game Property", icon='ZOOMIN')
        props.name = ''

        for i, prop in enumerate(game.properties):

            if is_font and i == prop_index:
                continue

            prop_box = box.box()
            row = prop_box.row()
            row.prop(prop, "name", text="")
            row.prop(prop, "type", text="")
            row.prop(prop, "value", text="")
            row.prop(prop, "show_debug", text="", toggle=True, icon='INFO')
            row.operator("object.game_property_remove", text="", icon='X', emboss=False).index = i


def register():
    bpy.utils.register_class(HivemapSelectionPanel)
    HivemapSelectionPanel.on_registered()
    bpy.app.handlers.scene_update_pre.append(tree_switcher)


def unregister():
    bpy.utils.unregister_class(HivemapSelectionPanel)
    HivemapSelectionPanel.on_unregistered()
    bpy.app.handlers.scene_update_pre.remove(tree_switcher)
