import bpy

class BlenderPopupButton(bpy.types.Operator):
  bl_idname = "node.hive_popup_button"
  bl_label = "<Hive Popup>"
  text = bpy.props.StringProperty()
  def execute(self, context):
    from .BlendManager import blendmanager
    blendmanager.popup_select(self.text)
    return {'FINISHED'}

    
class BlenderPopupMenu(bpy.types.Menu):
  bl_label = "Poll Mode" #not really generic, but we use it only for this atm... and you can't change it dynamically
  bl_idname = "NODE_MT_hive_popup_menu"
  bl_options = {'INTERNAL'}
  def draw(self, context):
    from .BlendManager import blendmanager    
    layout = self.layout    
    for option in blendmanager.popup_options:    
      b = BlenderPopupButton.bl_idname
      op = layout.operator(b, option)
      op.text = option

def register():
  bpy.utils.register_class(BlenderPopupMenu)
  bpy.utils.register_class(BlenderPopupButton)

def unregister():
  bpy.utils.unregister_class(BlenderPopupMenu)
  bpy.utils.unregister_class(BlenderPopupButton)

