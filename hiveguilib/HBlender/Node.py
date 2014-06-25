import bpy
import logging
from . import NodeSocket

_all_attributes = {}
_node_to_nodetree = {}


class HiveNode:
    bl_icon = 'NODETREE'
    bl_generic_sockets = True

    # Copy function to initialize a copied node from an existing one.
    def copy(self, node):
        blend_nodetree_manager = self.get_hgui_blend_nodetree_manager()
        if blend_nodetree_manager is None:
            logging.debug("Couldn't find Nodetree for node to copy")
            return

        logging.debug("Node pending copy")
        blend_nodetree_manager.canvas.h().mark_pending_copy(self)

    def set_attributes(self, attributes):
        self.inputs.clear()
        self.outputs.clear()

        for index, attribute in enumerate(attributes):
            name = attribute.name
            label = name
            if attribute.label is not None:
                label = attribute.label

            assert attribute.inhook or attribute.outhook  # TODO?
            if attribute.outhook:
                hook = attribute.outhook
                if attribute.inhook:
                    socktype = NodeSocket.socketclasses[hook.shape, hook.color, True]  # complementary socket

                else:
                    socktype = NodeSocket.socketclasses[hook.shape, hook.color]

                socket = self.outputs.new(socktype.bl_idname, name)
                socket.name = label
                socket.link_limit = 99
                socket.row = index + 1

            if attribute.inhook:
                hook = attribute.inhook
                socktype = NodeSocket.socketclasses[hook.shape, hook.color]
                socket = self.inputs.new(socktype.bl_idname, name)
                socket.name = label
                socket.link_limit = 99
                socket.row = index + 1

    def check_update(self):
        for socket in self.inputs:
            socket.check_update()

        for socket in self.outputs:
            socket.check_update()

    def find_input_socket(self, name):
        for socket in self.inputs:
            if socket.identifier == name:
                return socket

        raise AttributeError(name)

    def find_output_socket(self, name):
        for socket in self.outputs:
            if socket.identifier == name:
                return socket

        raise AttributeError(name)

    def get_hgui_blend_nodetree_manager(self):
        from . import BlendManager
        nodetree = self.id_data
        if nodetree is None:
            try:
                nodetree = _node_to_nodetree[self.bl_idname]
            except KeyError:
                return

        return BlendManager.blendmanager.get_nodetree_manager(nodetree.name)

    def get_hgui_node(self, blend_nodetree_manager):
        canvas = blend_nodetree_manager.canvas

        try:
            return canvas.get_node(self.name)

        except KeyError:
            return None

    def draw_buttons(self, context, layout):
        nodetree = self.id_data
        _node_to_nodetree[self.bl_idname] = nodetree
        if nodetree.nodes[0].name == self.name:
            nodetree.full_update()

        # This currently knows the first node is a node group, which represents the node tree #HACKY
        blend_nodetree_manager = self.get_hgui_blend_nodetree_manager()
        node = self.get_hgui_node(blend_nodetree_manager)

        # If we are a copy we need initialisation
        if node is None:
            return

        attributes = node.attributes
        try:
            layout.node_socket

        except AttributeError:
            return

        input_index = output_index = 0
        for index, attribute in enumerate(attributes):
            row = layout.row(align=True)
            row.label("NODE_NAME" + attribute.name)

            if attribute.inhook:
                row.node_socket(self.inputs[input_index])
                input_index += 1

            if attribute.outhook:
                row.node_socket(self.outputs[output_index])
                output_index += 1

    def draw_buttons_ext(self, context, layout):
        blend_nodetree_manager = self.get_hgui_blend_nodetree_manager()
        if blend_nodetree_manager is None:
            return

        # If we are a copy we need initialisation
        node = self.get_hgui_node(blend_nodetree_manager)
        if node is None:
            return

        blend_nodetree_manager.mainWin.h().draw_panel(context, layout)

    def __del__(self):
        try:
            pointer = self.as_pointer()
            if pointer in _all_attributes:
                del _all_attributes[pointer]
        except ReferenceError:
            return


class BaseNode(bpy.types.Node, HiveNode):
    """Base class for nodes in HIVE"""

    @classmethod
    def poll(cls, node_tree):
        """Determine if node can be added to a node tree"""
        nodetree_name = cls.bl_idname.rstrip("Node")
        return node_tree.bl_idname == nodetree_name


class HivemapNode(BaseNode):

    bl_idname = "HivemapNode"
    bl_label = bl_idname
    bl_generic_sockets = True
    bl_width_default = 50


class WorkermapNode(BaseNode):

    bl_idname = "WorkermapNode"
    bl_label = bl_idname


class SpydermapNode(BaseNode):

    bl_idname = "SpydermapNode"
    bl_label = bl_idname


def register():
    bpy.utils.register_class(HivemapNode)
    bpy.utils.register_class(WorkermapNode)
    bpy.utils.register_class(SpydermapNode)


def unregister():
    bpy.utils.unregister_class(HivemapNode)
    bpy.utils.unregister_class(WorkermapNode)
    bpy.utils.unregister_class(SpydermapNode)