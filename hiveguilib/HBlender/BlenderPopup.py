import bpy
from contextlib import contextmanager


class BlenderPopupButton(bpy.types.Operator):
    bl_idname = "node.hive_popup_button"
    bl_label = "<Hive Popup>"
    text = bpy.props.StringProperty()

    def execute(self, context):
        from .BlendManager import blendmanager

        blendmanager.popup_select(self.text)
        return {'FINISHED'}


class BlenderPopupMenu_(bpy.types.Menu):
    bl_label = "<Hive Popup>"
    bl_idname = "NODE_MT_hive_popup_menu"
    bl_options = {'INTERNAL'}

    def draw(self, context):
        from .BlendManager import blendmanager

        layout = self.layout
        for option in blendmanager.popup_options:
            b = BlenderPopupButton.bl_idname
            op = layout.operator(b, option)
            op.text = option


class BlenderPopupMenu:

    @staticmethod
    @contextmanager
    def factory(title):
        """Create a temporary popup menu class for displaying a custom title

        :param title: title of menu
        """
        popup_idname = "{}_{}".format(BlenderPopupMenu_.bl_label, title.strip(" "))
        custom_menu = type(popup_idname, (BlenderPopupMenu_,), {"bl_label": title, "bl_idname": popup_idname})
        bpy.utils.register_class(custom_menu)
        yield custom_menu
        bpy.utils.unregister_class(custom_menu)


def register():
    bpy.utils.register_class(BlenderPopupButton)


def unregister():
    bpy.utils.unregister_class(BlenderPopupButton)

