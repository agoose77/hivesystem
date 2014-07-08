import bpy
import bpy_extras
import logging
import copy

from . import level
from . import Operators


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


class FakeLink:

    def __init__(self, from_node, from_socket, to_node, to_socket):
        self.from_node = from_node
        self.from_socket = from_socket
        self.to_node = to_node
        self.to_socket = to_socket

    def __hash__(self):
        return hash(self.to_tuple())

    def __eq__(self, other):
        assert isinstance(other, self.__class__)
        logging.debug("Using __eq__ of FakeLink")
        return self.to_tuple() == other.to_tuple()

    def to_tuple(self):
        return self.from_node, self.from_socket, self.to_node, self.to_socket

    @classmethod
    def from_link(cls, link):
        return cls(
            link.from_node,
            link.from_socket,
            link.to_node,
            link.to_socket,
        )


def debugger(func):
    name = func.__qualname__
    def wrapper(self, *args, **kwargs):
        print("Calling {}, current node names: {}".format(name, [x.name for x in self.nodes.values()]))
        return func(self, *args, **kwargs)
    return wrapper


class HiveNodeTree:
    """Base class for HIVE node tree"""

    registered_name = bpy.props.StringProperty()

    def _check_deletions(self):
        """Poll the node tree and determine if any Blender nodes were deleted"""
        bntm = BlendManager.blendmanager.get_nodetree_manager(self.name)
        canvas = bntm.canvas

        gui_node_ids = [node.name for node in self.nodes]
        hblender_canvas_node_ids = canvas.h()._nodes
        removed_node_ids = list(set(hblender_canvas_node_ids).difference(gui_node_ids))

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
                if not link.use_socket_color:
                    self.links.remove(link)
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
            if not link.from_node.name in hcanvas._nodes and not link.to_node.name in hcanvas._nodes:
                continue

            attempt_success = hcanvas.gui_adds_connection(link, False)
            print("Trying to add", attempt_success)
            if attempt_success:
                changed_nodes.append(link.from_node)
                changed_nodes.append(link.to_node)

            else:
                self.links.remove(link)

        for link in removed_connections:
            if link.from_node.name in deletions or link.to_node.name in deletions:
                continue

            print(removed_connections)
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

    def _check_for_blender_copies(self):
        """Handle any Blender-clipboard pasted nodes (we need to register them into our internal model"""
        blend_nodetree_manager = BlendManager.blendmanager.get_nodetree_manager(self.name)
        canvas = blend_nodetree_manager.canvas
        blender_canvas = canvas.h()

        copied_nodes = {}

        # Scrape node tree and find copied nodes
        for node in list(self.nodes):
            node_id = node.name
            if node_id in blender_canvas._nodes:
                continue

            source_node_id = node.label
            copied_nodes[source_node_id] = node

        canvas.h().on_copy_nodes(copied_nodes)

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

            if not id_ in blender_canvas._nodes:
                continue

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

        self._check_for_blender_copies()
        deletions = self._check_deletions()
        self._check_links(deletions)

    def scene_update(self):

        bntm = BlendManager.blendmanager.get_nodetree_manager(self.name)
        canvas = bntm.canvas
        hcanvas = canvas.h()

        if hcanvas._busy:
            return

        self._check_positions()
        self._check_selection()

    def full_update(self):
        """We have been triggered from Node.draw_buttons, so we are in an unprivileged "draw" context.
        Therefore, don't do this stuff right away, but schedule it for the next scene update
        
        self._check_positions()
        self._check_selection()
        """

        BlendManager.blendmanager.schedule(self.scene_update)

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


def register():
    bpy.utils.register_class(HivemapNodeTree)
    bpy.utils.register_class(WorkermapNodeTree)
    bpy.utils.register_class(SpydermapNodeTree)


def unregister():
    bpy.utils.unregister_class(HivemapNodeTree)
    bpy.utils.unregister_class(WorkermapNodeTree)
    bpy.utils.unregister_class(SpydermapNodeTree)