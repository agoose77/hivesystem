import bpy
import logging
from . import NodeSocket

_all_attributes = {}


class HiveNode:
    bl_icon = 'NODETREE'
    bl_generic_sockets = True

    # Copy function to initialize a copied node from an existing one.
    def copy(self, node):
        raise NotImplementedError

    def set_attributes(self, attributes):
        for anr, a in enumerate(attributes):
            name = a.name
            label = name
            if a.label is not None:
                label = a.label

            assert a.inhook or a.outhook  # TODO?
            if a.outhook:
                h = a.outhook
                if a.inhook:
                    socktype = NodeSocket.socketclasses[h.shape, h.color, True]  # complementary socket
                else:
                    socktype = NodeSocket.socketclasses[h.shape, h.color]
                sock = self.outputs.new(socktype.bl_idname, name)
                sock.name = label
                sock.link_limit = 99
                sock.row = anr + 1

            if a.inhook:
                h = a.inhook
                socktype = NodeSocket.socketclasses[h.shape, h.color]
                sock = self.inputs.new(socktype.bl_idname, name)
                sock.name = label
                sock.link_limit = 99
                sock.row = anr + 1

    def check_update(self):
        for s in self.inputs: s.check_update()
        for s in self.outputs: s.check_update()

    def find_input_socket(self, name):
        for s in self.inputs:
            if s.identifier == name: return s
        raise AttributeError(name)

    def find_output_socket(self, name):
        for s in self.outputs:
            if s.identifier == name: return s
        raise AttributeError(name)

    def draw_buttons(self, context, layout):
        from . import BlendManager

        nodetree = self.id_data
        bntm = BlendManager.blendmanager.get_nodetree_manager(nodetree.name)
        if nodetree.nodes[0].label == self.label:
            nodetree.full_update()
        node = bntm.canvas.get_node(self.label)
        attributes = node.attributes

        try:
            layout.node_socket
        except AttributeError:
            return

        incounter, outcounter = 0, 0
        for anr, a in enumerate(attributes):
            row = layout.row(align=True)
            row.label("NODE_NAME" + a.name)
            if a.inhook:
                row.node_socket(self.inputs[incounter])
                incounter += 1
            if a.outhook:
                row.node_socket(self.outputs[outcounter])
                outcounter += 1

    def draw_buttons_ext(self, context, layout):
        from . import BlendManager

        nodetree = self.id_data
        bntm = BlendManager.blendmanager.get_nodetree_manager(nodetree.name)
        bntm.mainWin.h().draw_panel(context, layout)

    def __del__(self):
        p = self.as_pointer()
        if p in _all_attributes: del _all_attributes[p]


class HivemapNode(bpy.types.Node, HiveNode):
    bl_idname = "HivemapNode"
    bl_label = bl_idname
    bl_generic_sockets = True
    bl_width_default = 50

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'Hivemap'


class WorkermapNode(bpy.types.Node, HiveNode):
    bl_idname = "WorkermapNode"
    bl_label = bl_idname

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'Workermap'


class SpydermapNode(bpy.types.Node, HiveNode):
    bl_idname = "SpydermapNode"
    bl_label = bl_idname

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'Spydermap'


def register():
    bpy.utils.register_class(HivemapNode)
    bpy.utils.register_class(WorkermapNode)
    bpy.utils.register_class(SpydermapNode)


def unregister():
    bpy.utils.unregister_class(HivemapNode)
    bpy.utils.unregister_class(WorkermapNode)
    bpy.utils.unregister_class(SpydermapNode)
    