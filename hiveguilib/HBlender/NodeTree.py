import bpy
import bpy_extras
import logging
import copy

from . import level


def tag_redraw_area(tree_name):
    """Ask Blender to redraw node area for node tree

    :param tree_name: name of node tree
    """
    if bpy.context.screen is not None:
        for area in bpy.context.screen.areas:
            space = area.spaces[0]
            if space.type != 'NODE_EDITOR':
                continue

            if space.edit_tree.name != tree_name:
                continue

            area.tag_redraw()


class ChangeHiveLevel(bpy.types.Operator):
    """Handles keyboard events to change HIVE level with TAB / SHIFT TAB"""

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


class HiveToolsMenu(bpy.types.Menu):
    """Tools menu for HIVE operations"""
    bl_label = "Hive Options"
    bl_idname = "NODE_MT_hive_menu"

    def draw(self, context):
        layout = self.layout

        layout.prop(context.screen, "use_hive")
        layout.operator("wm.open_mainfile", text="Import map")
        layout.operator("wm.open_mainfile", text="Export map")


class HiveMapImport(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "hive.import_map"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import Hive Map"

    # ImportHelper mixin class uses this
    filename_ext = ".txt"

    filter_glob = bpy.props.StringProperty(default="*.web", options={'HIDDEN'})

    def execute(self, context):
        return
        return read_some_data(context, self.filepath)


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
    """Base class for HIVE node tree"""

    def _check_deletions(self):
        """Poll the node tree and determine if any Blender nodes were deleted"""
        bntm = BlendManager.blendmanager.get_nodetree_manager(self.name)
        canvas = bntm.canvas

        gui_node_ids = [node.name for node in self.nodes]
        hblender_canvas_node_ids = canvas.h()._nodes
        removed_node_ids = list(set(hblender_canvas_node_ids).difference(gui_node_ids))

        logging.debug("Removing nodes [" + ', '.join(removed_node_ids) + "]")

        if removed_node_ids:
            success = canvas.gui_removes_nodes(removed_node_ids)
            assert success

        return removed_node_ids

    def _check_links(self, deletions):
        """Poll the node tree and determine if any connections between Blender nodes were modified

        :param deletions: deleted node ids
        """
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

    def _check_copying(self):
        """Handle any Blender-clipboard pasted nodes (we need to register them into our internal model"""
        blend_nodetree_manager = BlendManager.blendmanager.get_nodetree_manager(self.name)
        canvas = blend_nodetree_manager.canvas

        canvas.h().on_copy_nodes()

    def _check_positions(self):
        """Handle any Blender nodes moved in the Blender UI"""
        blend_nodetree_manager = BlendManager.blendmanager.get_nodetree_manager(self.name)
        canvas = blend_nodetree_manager.canvas
        hcanvas = canvas.h()
        positions = hcanvas._positions

        for node in self.nodes:
            name = node.name

            if positions.get(name) != node.location:
                positions[name] = position = copy.copy(node.location)
                hcanvas.gui_moves_node(name, position)

    def _copy_pending_nodes(self):
        """Copy any pending nodes into the clipboard

        Workaround for single-copy operations overwriting clipboard for multiple copies
        """
        blend_nodetree_manager = BlendManager.blendmanager.get_nodetree_manager(self.name)
        canvas = blend_nodetree_manager.canvas
        canvas.h().copy_pending_nodes()

    def _check_selection(self):
        """Handle any Blender nodes selected in the Blender UI"""
        bntm = BlendManager.blendmanager.get_nodetree_manager(self.name)
        canvas = bntm.canvas
        blender_canvas = canvas.h()
        selected = []
        changed = False
        selections = blender_canvas._selection

        for node in self.nodes:
            id_ = node.name

            if id_ not in selections:
                selections[id_] = bool(node.select)

                if selections[id_]:
                    selected.append(id_)
                    changed = True

            elif selections[id_] != node.select:
                if node.select:
                    selected.append(id_)

                changed = True
                selections[id_] = bool(node.select)

        if not changed:
            return

        if selected:
            operation_success = canvas.gui_selects(selected)

        else:
            operation_success = canvas.gui_deselects()

        assert operation_success

        tag_redraw_area(self.name)

    def find_node(self, name):
        """Find Blender node with name

        :param name: name of Blender node
        """
        for node in self.nodes:
            if node.name == name:
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
        BlendManager.blendmanager.schedule(self._check_copying)
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


def draw_hive_menu(self, context):
    if context.space_data.tree_type == "Hivemap":
        self.layout.menu("NODE_MT_hive_menu")


def draw_hive_level(self, context):
    if BlendManager.use_hive_get(context) and context.space_data.tree_type == "Hivemap":
     #   self.layout.label("Hive Level")
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
    bpy.utils.register_class(HiveMapImport)
    bpy.utils.register_class(ChangeHiveLevel)
    bpy.utils.register_class(HiveToolsMenu)

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

    bpy.types.NODE_HT_header.append(draw_hive_menu)
    bpy.types.NODE_HT_header.append(draw_hive_level)
    bpy.types.NODE_HT_header.append(draw_spyderhive)
    bpy.types.NODE_HT_header.append(check_tab_control)


def unregister():
    bpy.utils.unregister_class(HivemapNodeTree)
    bpy.utils.unregister_class(WorkermapNodeTree)
    bpy.utils.unregister_class(SpydermapNodeTree)
    bpy.utils.unregister_class(ChangeHiveLevel)
    bpy.utils.unregister_class(HiveMapImport)
    bpy.utils.unregister_class(HiveToolsMenu)

    bpy.types.NODE_HT_header.remove(draw_hive_level)
    bpy.types.NODE_HT_header.remove(draw_spyderhive)
    bpy.types.NODE_HT_header.remove(check_tab_control)
    bpy.types.NODE_HT_header.remove(draw_hive_menu)

if __name__ == "__main__":
    unregister()
    register()