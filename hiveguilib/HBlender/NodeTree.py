import bpy
import logging
import copy

from . import level


class ChangeHiveLevel(bpy.types.Operator):
    """Handles keyboard events to change HIVE level"""

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

        hive_levels = [int(x[0]) for x in bpy.types.Screen.hive_level[1]["items"]]
        hive_level = int(context.screen.hive_level) + direction

        # Clamp level
        if hive_level < hive_levels[0]:
            hive_level = hive_levels[-1]

        elif hive_level > hive_levels[-1]:
            hive_level = hive_levels[0]

        context.screen.hive_level = str(hive_level)

        self.held = True

        return {"PASS_THROUGH"}


class FakeLink:

    def __init__(self, from_node, from_socket, to_node, to_socket):
        self.from_node = from_node
        self.from_socket = from_socket
        self.to_node = to_node
        self.to_socket = to_socket

    @classmethod
    def from_link(cls, link):
        return cls(
            link.from_node,
            link.from_socket,
            link.to_node,
            link.to_socket,
        )


class HiveNodeTree:

    def _check_deletions(self):
        # TODO REMOVE THIS
        import logging
        # For debugging in Blender
        logging.t = self

        bntm = BlendManager.blendmanager.get_nodetree_manager(self.name)
        canvas = bntm.canvas

        gui_node_ids = [node.label for node in self.nodes]
        hblender_canvas_node_ids = canvas.h()._nodes
        removed_node_ids = list(set(hblender_canvas_node_ids).difference(gui_node_ids))

        logging.debug("Removing nodes [" + ', '.join(removed_node_ids) + "]")

        if removed_node_ids:
            success = canvas.gui_removes_nodes(removed_node_ids)
            assert success
        return removed_node_ids

    def _check_links(self, deletions):
        bntm = BlendManager.blendmanager.get_nodetree_manager(self.name)
        hcanvas = bntm.canvas.h()

        attempted_new_connections = []
        removed_connections = []

        # Links in editor that don't exist in the HIVE internal model
        hive_links = {(l.from_node, l.from_socket, l.to_node, l.to_socket) for l in hcanvas._links}
        for link in list(self.links):
            pair = link.from_node, link.from_socket, link.to_node, link.to_socket
            if pair in hive_links:
                continue

            attempted_new_connections.append(link)

        # Links in internal model which no longer exist in the editor
        blender_links = {(l.from_node, l.from_socket, l.to_node, l.to_socket) for l in self.links}
        for link in hcanvas._links:
            pair = link.from_node, link.from_socket, link.to_node, link.to_socket
            if pair in blender_links:
                continue

            removed_connections.append(link)

        changed_nodes = []
        for link in attempted_new_connections:
            attempt_success = hcanvas.gui_adds_connection(link, False)

            if attempt_success:
                changed_nodes.append(link.from_node)
                changed_nodes.append(link.to_node)

            else:
                self.links.remove(link)

        for link in removed_connections:
            if link.from_node.label in deletions or link.to_node.label in deletions:
                continue

            attempt_success = hcanvas.gui_removes_connection(link)

            if attempt_success:
                changed_nodes.append(link.from_node)
                changed_nodes.append(link.to_node)

            else:
                logging.debug("removal of connection was disapproved, what to do?")

        # Handle node connection updates
        for node in changed_nodes:
            node.check_update()

        hcanvas._links = {FakeLink.from_link(l) for l in self.links}

    def _check_positions(self):
        blend_nodetree_manager = BlendManager.blendmanager.get_nodetree_manager(self.name)
        canvas = blend_nodetree_manager.canvas
        hcanvas = canvas.h()
        positions = hcanvas._positions

        for node in self.nodes:
            label = node.label

            if positions.get(label) != node.location:
                positions[label] = position = copy.copy(node.location)
                hcanvas.gui_moves_node(label, position)

    def _copy_pending_nodes(self):
        blend_nodetree_manager = BlendManager.blendmanager.get_nodetree_manager(self.name)
        canvas = blend_nodetree_manager.canvas
        canvas.h().copy_pending_nodes()

    def _check_selection(self):
        bntm = BlendManager.blendmanager.get_nodetree_manager(self.name)
        canvas = bntm.canvas
        hcanvas = canvas.h()
        selected = []
        changed = False
        selections = hcanvas._selection
        for node in self.nodes:
            label = node.label
            if label not in selections:
                selections[label] = bool(node.select)
                if selections[label]:
                    selected.append(label)
                    changed = True

            elif selections[label] != node.select:
                if node.select:
                    selected.append(label)
                changed = True
                selections[label] = bool(node.select)

        if not changed:
            return

        if selected:
            operation_success = canvas.gui_selects(selected)

        else:
            operation_success = canvas.gui_deselects()

        assert operation_success

        if bpy.context.screen is not None:
            for area in bpy.context.screen.areas:
                space = area.spaces[0]
                if space.type != 'NODE_EDITOR':
                    continue

                if space.edit_tree.name != self.name:
                    continue

                area.tag_redraw()

    def find_node(self, name):
        for node in self.nodes:
            if node.label == name:
                return node

        raise AttributeError(name)

    def update(self):
        if BlendManager.blendmanager._loading:
            return

        bntm = BlendManager.blendmanager.get_nodetree_manager(self.name)
        canvas = bntm.canvas
        hcanvas = canvas.h()

        if hcanvas._busy:
            return

        deletions = self._check_deletions()
        self._check_links(deletions)

    def full_update(self):
        """We have been triggered from Node.draw_buttons, so we are in an unprivileged "draw" context.
        Therefore, don't do this stuff right away, but schedule it for the next scene update
        
        self._check_positions()
        self._check_selection()
        """
        BlendManager.blendmanager.schedule(self._check_positions)
        BlendManager.blendmanager.schedule(self._check_selection)
        BlendManager.blendmanager.schedule(self._copy_pending_nodes)

from . import BlendManager


class HivemapNodeTree(bpy.types.NodeTree, HiveNodeTree):
    # Description string
    '''This NodeTree describes a Hive system hivemap'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'Hivemap'
    # Label for nice name display
    bl_label = 'Hive system hivemap'
    # Icon identifier
    bl_icon = 'LOGIC'


class WorkermapNodeTree(bpy.types.NodeTree, HiveNodeTree):
    # Description string
    '''This NodeTree describes a Hive system workermap'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'Workermap'
    # Label for nice name display
    bl_label = 'Hive system workermap'
    # Icon identifier
    bl_icon = 'FORCE_MAGNETIC'

    @classmethod
    def poll(cls, context):
        return level.active_workergui(context)


class SpydermapNodeTree(bpy.types.NodeTree, HiveNodeTree):
    # Description string
    '''This NodeTree describes a Hive system spydermap'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'Spydermap'
    # Label for nice name display
    bl_label = 'Hive system spydermap'
    # Icon identifier
    bl_icon = 'FORCE_LENNARDJONES'

    @classmethod
    def poll(cls, context):
        return level.active_spydergui(context)


def draw_use_hive(self, context):
    if context.space_data.tree_type == "Hivemap":
        self.layout.prop(context.screen, "use_hive")


def draw_hive_level(self, context):
    if BlendManager.use_hive_get(context):
        self.layout.label("Hive level")
        self.layout.prop(context.screen, "hive_level", text="")


def draw_spyderhive(self, context):
    blend_manager = BlendManager.blendmanager
    if context.space_data.tree_type == "Spydermap" and context.space_data.edit_tree is not None:
        blend_manager.spyderhive_widget.draw(context, self.layout)


def check_tab_control(self, context):
    if context.screen.use_hive:
        if ChangeHiveLevel.can_invoke():
            bpy.ops.node.change_hive_level("INVOKE_DEFAULT")

    else:
        if not ChangeHiveLevel.can_invoke():
            ChangeHiveLevel.disable()


def register():
    bpy.utils.register_class(HivemapNodeTree)
    bpy.utils.register_class(WorkermapNodeTree)
    bpy.utils.register_class(SpydermapNodeTree)
    bpy.utils.register_class(ChangeHiveLevel)
    bpy.types.Screen.use_hive = bpy.props.BoolProperty(
        name="Use Hive Logic",
        description="Enables the Hive system in the Game Engine for this scene",
        get=BlendManager.use_hive_get,
        set=BlendManager.use_hive_set,
    )
    bpy.types.Screen.hive_level = bpy.props.EnumProperty(
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
    bpy.types.NODE_HT_header.append(draw_hive_level)
    bpy.types.NODE_HT_header.append(draw_use_hive)
    bpy.types.NODE_HT_header.append(draw_spyderhive)
    bpy.types.NODE_HT_header.append(check_tab_control)


def unregister():
    bpy.utils.unregister_class(HivemapNodeTree)
    bpy.utils.unregister_class(WorkermapNodeTree)
    bpy.utils.unregister_class(SpydermapNodeTree)
    bpy.utils.unregister_class(ChangeHiveLevel)
    bpy.types.NODE_HT_header.remove(draw_hive_level)
    bpy.types.NODE_HT_header.remove(draw_use_hive)
    bpy.types.NODE_HT_header.remove(draw_spyderhive)

if __name__ == "__main__":
    unregister()
    register()