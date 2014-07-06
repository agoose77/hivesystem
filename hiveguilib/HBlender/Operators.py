import bpy

class SynchroniseDataOperator(bpy.types.Operator):
    """Synchronise the text blocks and Node trees.

    First save all node trees to text, then reload all text files.
    """
    bl_idname = "hive.synchronise_data"
    bl_label = "Synchronise NodeTrees and TextBlocks"

    @classmethod
    def poll(cls, context):
        from . import BlendManager
        return BlendManager.use_hive_get(context)

    def execute(self, context):
        from . import BlendManager
        blend_manager = BlendManager.blendmanager

        blend_manager.blend_save()
        blend_manager._loading = True
        blend_manager.blend_load()

        return {'FINISHED'}


def register():
    bpy.utils.register_class(SynchroniseDataOperator)


def unregister():
    bpy.utils.unregister_class(SynchroniseDataOperator)


register()