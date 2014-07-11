import bpy

from collections import defaultdict
from . import scalepos, unscalepos


class AddHiveNode(bpy.types.Operator):
    bl_idname = "node.add_hive_node"
    bl_label = "Add a Hive system node to the Node Editor"

    type = bpy.props.StringProperty()

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            region = context.region
            # TODO update to 2.7 -> context.space_data.cursor_location_from_region(event.mouse_region_x, event.mouse_region_y)
            x, y = event.mouse_region_x - (region.width / 2), event.mouse_region_y - (region.height / 2)
            node = context.active_node
            if node is None:
                return {'FINISHED'}

            node.location = x, y

        elif event.type == 'LEFTMOUSE':
            return {'FINISHED'}

        elif event.type == 'RIGHTMOUSE':
            context.active_node.location = 0, 0
            return {'FINISHED'}

        elif event.type == 'ESC':
            nodetree = context.space_data.edit_tree
            node = context.active_node
            nodetree.nodes.remove(node)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        # In Qt, dragged widgets generate their own events
        #In Blender, we have to contact the clipboard directly
        from . import BlendManager

        nodetree_name = context.space_data.edit_tree.name

        add_node = bpy.types.NODE_OT_add_node
        add_node.store_mouse_cursor(context, event)

        x, y = unscalepos(context.space_data.cursor_location)

        blend_node_tree_manager = BlendManager.blendmanager.blend_nodetree_managers[nodetree_name]
        pwc = blend_node_tree_manager.pwc

        pwc._select_worker(tuple(self.type.split(".")))
        clip = blend_node_tree_manager.clipboard
        clip.drop_worker(x, y)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


class SynchroniseDataOperator(bpy.types.Operator):
    """Synchronise the text blocks and Node trees.

    First save all node trees to text, then reload all text files.
    """
    bl_idname = "hive.synchronise_data"
    bl_label = "Synchronise"

    @classmethod
    def poll(cls, context):
        from . import BlendManager
        return BlendManager.use_hive_get(context.scene)

    def execute(self, context):
        from . import BlendManager
        blend_manager = BlendManager.blendmanager

        blend_manager.blend_save()
        blend_manager._loading = True
        blend_manager.blend_load()

        return {'FINISHED'}


class RemoveBoundUsers(bpy.types.Operator):
    """Remove any references to this NodeTree from bound objects"""
    bl_idname = "hive.remove_bound_users"
    bl_label = "Remove users"

    @classmethod
    def poll(cls, context):
        from . import BlendManager
        return BlendManager.use_hive_get(context.scene)

    def execute(self, context):
        mapping = defaultdict(list)
        for obj in context.scene.objects:
            mapping[obj.hive_nodetree].append(obj)

        for space in (sp for s in bpy.data.screens for a in s.areas for sp in a.spaces if sp.type == "NODE_EDITOR"):
            node_tree = space.node_tree

            if node_tree is None:
                continue

            if space.tree_type != "Hivemap":
                continue

            if not node_tree.name in mapping:
                continue

            for obj in mapping[node_tree.name]:
                obj.hive_nodetree = ""

            break

        return {'FINISHED'}


class ChangeHiveLevel(bpy.types.Operator):
    """Handles keyboard events to change HIVE level with TAB | SHIFT TAB"""

    _running = []

    bl_idname = "node.change_hive_level"
    bl_label = "Change the HIVE system level"

    @classmethod
    def check_valid(cls):
        invalid = []
        for registered in cls._running:
            try:
                registered.as_pointer
            except ReferenceError:
                invalid.append(registered)

        for registered in invalid:
            cls._running.remove(registered)

    @classmethod
    def can_invoke(cls):
        cls.check_valid()
        return not cls._running

    @classmethod
    def disable(cls):
        cls.check_valid()
        for registered in cls._running:
            registered.invalid = True
        cls._running.clear()

    def invoke(self, context, event):
        if not ChangeHiveLevel.can_invoke():
            return {"CANCELLED"}

        ChangeHiveLevel._running.append(self)

        self.held = False
        self.invalid = False

        return self.execute(context)

    def execute(self, context):
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    @staticmethod
    def is_node_editor(context, event):
        """Determine if the event occurred within the node editor

        :param context: event context
        :param event: event instance
        """
        node_editor = next((x for x in context.window.screen.areas.values() if x.type == "NODE_EDITOR"), None)
        if node_editor is None:
            return False

        return node_editor.x <= event.mouse_x <= (node_editor.x + node_editor.width) and \
               node_editor.y <= event.mouse_y <= (node_editor.y + node_editor.height)

    def modal(self, context, event):
        if self.invalid:
            return {"CANCELLED"}

        if event.value == "RELEASE":
            self.held = False
            return {"PASS_THROUGH"}

        elif event.value != 'PRESS' or self.held or not self.is_node_editor(context, event):
            return {"PASS_THROUGH"}

        if not event.type == "TAB":
            return {"PASS_THROUGH"}

        direction = (-2 * event.shift) + 1

        hive_levels = [int(x[0]) for x in bpy.types.Scene.hive_level[1]["items"]]
        hive_level = int(context.scene.hive_level) + direction

        # Clamp level
        if hive_level < hive_levels[0]:
            hive_level = hive_levels[-1]

        elif hive_level > hive_levels[-1]:
            hive_level = hive_levels[0]

        context.scene.hive_level = str(hive_level)

        self.held = True

        return {"PASS_THROUGH"}


def register():
    bpy.utils.register_class(SynchroniseDataOperator)
    bpy.utils.register_class(ChangeHiveLevel)
    bpy.utils.register_class(RemoveBoundUsers)
    bpy.utils.register_class(AddHiveNode)


def unregister():
    bpy.utils.unregister_class(SynchroniseDataOperator)
    bpy.utils.unregister_class(ChangeHiveLevel)
    bpy.utils.unregister_class(RemoveBoundUsers)
    bpy.utils.unregister_class(AddHiveNode)