import bpy

from . import BlendManager
from .NodeTrees import SpydermapNodeTree, HiveNodeTree
from .Operators import ChangeHiveLevel, RemoveBoundUsers


class HiveToolsMenu(bpy.types.Menu):
    """Tools menu for HIVE operations"""
    bl_label = "Hive Options"
    bl_idname = "NODE_MT_hive_menu"

    def draw(self, context):
        layout = self.layout

        layout.prop(context.scene, "use_hive")

        row = layout.column()
        row.prop(context.scene, "switch_to_bound_hive_tree")
        row.operator("hive.synchronise_data", icon="FILE_REFRESH")
        row.operator("hive.remove_bound_users", icon="X")
        row.active = context.scene.use_hive


def draw_hive_menu(self, context):
    self.layout.menu("NODE_MT_hive_menu")


def draw_hive_level(self, context):
    if BlendManager.use_hive_get(context.scene):
        self.layout.prop(context.scene, "hive_level", text="")


def draw_spyderhive(self, context):
    blend_manager = BlendManager.blendmanager
    if isinstance(context.space_data.edit_tree, SpydermapNodeTree):
        blend_manager.spyderhive_widget.draw(context, self.layout)


def draw_docstring(self, context):
    blend_manager = BlendManager.blendmanager
    if isinstance(context.space_data.edit_tree, HiveNodeTree):
        blend_manager.docstring_widget.draw(context, self.layout)


def check_tab_control(self, context):
    """Determine if the Hive level modal operator keyboard listener should be running"""
    if BlendManager.use_hive_get(context.scene):
        if ChangeHiveLevel.can_invoke():
            bpy.ops.node.change_hive_level("INVOKE_DEFAULT")

    elif not ChangeHiveLevel.can_invoke():
        ChangeHiveLevel.disable()


header_draw_functions = draw_hive_menu, draw_hive_level, draw_spyderhive, check_tab_control#, draw_docstring


def register():
    bpy.utils.register_class(HiveToolsMenu)

    bpy.types.Scene.use_hive = bpy.props.BoolProperty(
        name="Use Hive Logic",
        description="Enables the Hive system in the Game Engine for this scene",
        get=BlendManager.use_hive_get,
        set=BlendManager.use_hive_set,
    )

    bpy.types.Scene.switch_to_bound_hive_tree = bpy.props.BoolProperty(
        name="Set NodeTree from object",
        description="Enables the Hive system to use the read the bound NodeTree from the active object")

    bpy.types.Scene.hive_level = bpy.props.EnumProperty(
        name="Hive level",
        description="Hive logic level, unlocks more advanced hive features",
        items=(
            ("1", "1: SPARTA", "Level 1: Only use standard SPARTA nodes", 1),
            ("2", "2: Advanced SPARTA", "Level 2: Use all SPARTA nodes and parameters", 2),
            ("3", "3: Dragonfly", "Level 3: Also use Dragonfly nodes", 3),
            ("4", "4: Custom workers", "Level 4: Enable custom worker GUI", 4),
            ("5", "5: Spyder hives", "Level 5: Enable Spyder hive GUI for custom configuration", 5),
            ("6", "6: Advanced", "Level 6: Enable blocks, wasps and other advanced hive features", 6),
        ),
        update=BlendManager.change_hive_level
    )

    for function in header_draw_functions:
        bpy.types.NODE_HT_header.append(function)


def unregister():
    bpy.utils.unregister_class(HiveToolsMenu)

    for function in header_draw_functions:
        bpy.types.NODE_HT_header.remove(function)