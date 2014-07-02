import bpy
from contextlib import contextmanager


class BlenderPopupButton(bpy.types.Operator):
    bl_idname = "node.hive_popup_button"
    bl_label = "<Hive Popup>"

    # Custom properties
    caller = bpy.props.StringProperty(description="ID of caller menu")
    option = bpy.props.StringProperty(description="Option to invoke callback with")

    def execute(self, context):
        from .BlendManager import blendmanager

        options, callback = blendmanager.get_popup_data(self.caller)
        callback(self.option)

        return {'FINISHED'}


class BlenderPopupMenu_(bpy.types.Menu):
    bl_label = "<Hive Popup>"
    bl_idname = "NODE_MT_hive_popup_menu"
    bl_options = {'INTERNAL'}

    def draw(self, context):
        layout = self.layout
        from .BlendManager import blendmanager

        options, callback = blendmanager.get_popup_data(self.bl_idname)

        # Show menu options
        for option in options:
            operator_id = BlenderPopupButton.bl_idname
            operator = layout.operator(operator_id, option)
            operator.caller = self.bl_idname
            operator.option = option


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

