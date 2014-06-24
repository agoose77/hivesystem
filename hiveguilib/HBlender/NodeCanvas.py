from ..HUtil.Node import h_map_node
from .NodeTree import FakeLink
from . import Node, NodeSocket, NodeTree, scalepos, unscalepos
import logging


def nullfunc(*args, **kwargs):
    pass


def new_connection():
    n = 0
    while 1:
        n += 1
        yield "connection-%d" % n


class NodeCanvas:
    _hgui = None
    _connection_generator = new_connection()

    def __init__(self, mainWindow, clipboard, statusbar):
        self._statusbar = statusbar
        self._nodes = {}
        self._connections = {}
        self._selection = {}  # dict of node names (RNA Node labels), set by NodeTree
        self._positions = {}  # dict, set by NodeTree
        self._labels = []
        self._links = set()
        self._busy = False
        self.bntm = None

        import logging
        logging.nodecanvas = self

    def set_blendnodetreemanager(self, blendnodetreemanager):
        self.bntm = blendnodetreemanager

    def get_nodeclass(self):
        tree = self.bntm.get_nodetree()
        if isinstance(tree, NodeTree.HivemapNodeTree):
            return Node.HivemapNode

        if isinstance(tree, NodeTree.SpydermapNodeTree):
            return Node.SpydermapNode

        if isinstance(tree, NodeTree.WorkermapNodeTree):
            return Node.WorkermapNode

        raise ValueError(tree.bl_idname)

    def _add_node(self, id_, name, attributes, position, tooltip):
        self._busy = True
        try:
            nodetree = self.bntm.get_nodetree()
            nodeclass = self.get_nodeclass()
            node = nodetree.nodes.new(nodeclass.bl_idname)
            node.label = name
            node.location = position
            self._labels.append(name)
            node.set_attributes(attributes)
            nodetree.nodes.active = node

        finally:
            self._busy = False

    def h_add_node(self, id_, hnode):
        mapnode = h_map_node(hnode)
        pos = scalepos(mapnode.position)
        self._add_node(id_, mapnode.name, mapnode.attributes, pos, mapnode.tooltip)
        self._nodes[id_] = mapnode

    def h_morph_node(self, id_, hnode, mapcon):
        mapnode = h_map_node(hnode)
        pos = scalepos(mapnode.position)
        node = self._nodes[id_]
        node.attributes = mapnode.attributes

        nodetree = self.bntm.get_nodetree()
        node = [n for n in nodetree.nodes if n.label == node.name][0]

        self._busy = True
        in_out_attributes = [a.name for a in mapnode.attributes if a.inhook is not None and a.outhook is not None]
        matched_inputs = set()
        matched_outputs = set()
        accounted_inputs = set()
        accounted_outputs = set()

        for attribute_name_a, attribute_name_b, mode in mapcon:
            assert mode in ("in", "out"), mode
            if mode == "in":
                at0 = node.find_input_socket(attribute_name_a)
                matched_inputs.add(attribute_name_a)
                accounted_inputs.add(attribute_name_b)

            else:
                at0 = node.find_output_socket(attribute_name_a)
                matched_outputs.add(attribute_name_a)
                accounted_outputs.add(attribute_name_b)
            print(mapnode.attributes)
            at0.name = [n for n in mapnode.attributes if n.name == attribute_name_b][0].label

        # Remove unmatched sockets
        # This should be safe: attributes with connections won't be allowed to be deleted
        change = True
        while change:
            change = False
            for a in node.inputs:
                if a.name not in matched_inputs:
                    node.inputs.remove(a)
                    change = True

        change = True
        while change:
            change = False
            for a in node.outputs:
                if a.name not in matched_outputs:
                    node.inputs.remove(a)
                    change = True

        #Create new sockets that didn't exist before
        for a in mapnode.attributes:
            label = a.name
            if a.label is not None: label = a.label
            if a.outhook:
                if a.name in accounted_outputs: continue
                h = a.outhook
                if a.inhook:
                    socktype = NodeSocket.socketclasses[h.shape, h.color, True]  #complementary socket
                else:
                    socktype = NodeSocket.socketclasses[h.shape, h.color]

                sock = node.outputs.new(socktype.bl_idname, a.name)
                sock.name = label
                sock.link_limit = 99

            if a.inhook:
                if a.name in accounted_inputs:
                    continue
                h = a.inhook
                socktype = NodeSocket.socketclasses[h.shape, h.color]
                sock = node.inputs.new(socktype.bl_idname, a.name)
                sock.name = label
                sock.link_limit = 99

        #Assign the correct rows
        inputpos = 0
        outputpos = 0
        for anr, a in enumerate(mapnode.attributes):
            if a.inhook:
                sock = node.inputs[inputpos]
                sock.row = anr + 1
                inputpos += 1
            if a.outhook:
                sock = node.outputs[outputpos]
                sock.row = anr + 1
                outputpos += 1

        self._busy = False

    def gui_moves_node(self, id_, position):
        ret = True
        if self._hgui is not None:
            ret = self._hgui().gui_moves_node(id_, unscalepos(position))
        return ret

    def select(self, ids):
        nodetree = self.bntm.get_nodetree()
        nodenames = [self._nodes[id].name for id in ids]
        for node in nodetree.nodes:
            if node.label in nodenames:
                node.select = True
            else:
                node.select = False

        if len(nodenames) == 1:
            nodename = nodenames[0]
            for node in nodetree.nodes:
                if node.label == nodename:
                    nodetree.nodes.active = node
                    break

    def remove_node(self, id_):
        import logging
        logging.debug("Removing node blendercanvas")
        self._busy = True
        if id_ in self._positions:
            self._positions.pop(id_)

        node = self._nodes.pop(id_)
        nodetree = self.bntm.get_nodetree()

        for nr, n in list(enumerate(nodetree.nodes)):
            if n.label != node.name:
                continue

            nodetree.nodes.remove(n)
            self._labels.pop(nr)
            break

        self._links = {FakeLink.from_link(l) for l in nodetree.links}
        self._busy = False

    def rename_node(self, old_id, new_id, new_name):
        self._busy = True
        node = self._nodes.pop(old_id)
        self._nodes[new_id] = node
        old_name = node.name
        node.name = new_name
        nodetree = self.bntm.get_nodetree()

        for nr, n in enumerate(nodetree.nodes):
            if n.label != old_name:
                continue

            n.label = new_name
            self._labels[nr] = new_name

            break

        if self._selection is not None and old_name in self._selection:
            pos = self._selection.pop(old_name)
            self._selection[new_name] = pos
            if self._hgui is not None:
                sel = [n for n in self._selection if self._selection[n]]
                selected_ids = [id_ for id_, n in self._nodes.items() if n.name in sel]
                self._hgui().gui_selects(selected_ids)

        self._busy = False

    def h_add_connection(self, id_, connection, valid):
        self._busy = True
        tree = self.bntm.get_nodetree()
        start_node = tree.find_node(connection.start_node)
        start = start_node.find_output_socket(connection.start_attribute)
        end_node = tree.find_node(connection.end_node)
        end = end_node.find_input_socket(connection.end_attribute)
        link = tree.links.new(start, end, False)
        assert link is not None, (
            (connection.start_node, connection.start_attribute),
            (connection.end_node, connection.end_attribute),
        )

        try:
            link.use_socket_color = True
            link.dashed = (link.from_socket._shape == "DIAMOND")

        except AttributeError:
            pass

        self._connections[id_] = connection
        self._links = {FakeLink.from_link(l) for l in tree.links}
        fl = FakeLink.from_link(link)
        self._links.add(fl)  # adding a new link goes slowly...
        start.check_update()
        end.check_update()
        self._busy = False

    def gui_adds_connection(self, link, force):
        from .BlendManager import blendmanager
        from functools import partial

        connection = self.map_link(link)
        con_id = next(self._connection_generator)
        ret = True
        if self._hgui is not None:

            f = self._hgui().pushpull_connection
            if force: f = nullfunc
            pollmodes = ["Manual", "Every tick", "On change"]
            funcs = []
            for pollmode in pollmodes:
                funcs.append(partial(f, connection, pollmode))
            blendmanager.popup_callbacks = funcs
            ret = self._hgui().gui_adds_connection(connection, con_id, force)
        if ret or force:
            self._connections[con_id] = connection
            link.use_socket_color = True
            link.dashed = (link.from_socket._shape == "DIAMOND")
        if force and not ret:
            # connection.setColor(disallowed_connection_color) #TODO
            link.use_socket_color = False
        return ret

    def gui_removes_connection(self, link):
        if self._hgui is None:
            return True

        if self._busy:
            return False

        logging.debug("in GUI_REMOVES_CONNECTION")

        connection = self.map_link(link)
        con_id = self.find_connection(connection)
        success = self._hgui().gui_removes_connection(con_id)
        if success:
            self._connections.pop(con_id)
        return success

    def remove_connection(self, id_):
        # This may not do anything, if Blender already deleted the links,
        # e.g. if the connected node was just deleted

        logging.debug("in REMOVE_CONNECTION")
        self._busy = True
        tree = self.bntm.get_nodetree()
        connection = self._connections.pop(id_)
        for link in tree.links:
            c = self.map_link(link)
            if c.start_node != connection.start_node:
                continue

            if c.end_node != connection.end_node:
                continue

            if c.start_attribute != connection.start_attribute:
                continue

            if c.end_attribute != connection.end_attribute:
                continue

            tree.links.remove(link)
        self._busy = False

    def set_statusbar_message(self, message):
        if self._statusbar is None: return
        self._statusbar.setMessage(message)

    def clear_statusbar_message(self):
        if self._statusbar is None: return
        self._statusbar.clearMessage()

    def set_attribute_value(self, id_, attribute, value):
        logging.debug("NodeCanvas.set_attribute_value, what to do?")

    def _change_attribute(self, id_, attribute, hidden):
        nodetree = self.bntm.get_nodetree()
        node = None
        for nr, n in enumerate(nodetree.nodes):
            if n.label != id_:
                continue

            node = n
            break
        assert node is not None, id_
        for io in (node.inputs, node.outputs):
            for sock in io:
                if sock.identifier == attribute:
                    sock.hide = hidden
                    return

    def show_attribute(self, id_, attribute):
        self._change_attribute(id_, attribute, hidden=False)

    def hide_attribute(self, id_, attribute):
        self._change_attribute(id_, attribute, hidden=True)

    def find_connection(self, connection):
        #TODO implement __eq__ on connections?
        for connection_id, connection_ in self._connections.items():
            if connection_.start_node != connection.start_node:
                continue
            if connection_.end_node != connection.end_node:
                continue
            if connection_.start_attribute != connection.start_attribute:
                continue
            if connection_.end_attribute != connection.end_attribute:
                continue
            return connection_id
        raise KeyError

    def map_link(self, link):
        from ..HGui import Connection

        start_node = link.from_node.label
        start_attribute = link.from_socket.identifier
        end_node = link.to_node.label
        end_attribute = link.to_socket.identifier
        return Connection(start_node, start_attribute, end_node, end_attribute, [], )
