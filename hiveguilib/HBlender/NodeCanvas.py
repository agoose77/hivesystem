from ..HUtil.Node import h_map_node
from .NodeTree import FakeLink
from .BlendNodeTreeManager import HiveMapNodeTreeManager, WorkerMapNodeTreeManager, SpyderMapNodeTreeManager
from . import Node, NodeSocket, NodeTree, scalepos, unscalepos
import logging
import bpy


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
        self._pending_copy = set()
        self._labels = []
        self._links = set()
        self._busy_stack = []
        self.bntm = None

    @property
    def _busy(self):
        """Check the busy stack and determine if we're in the middle of an operation"""
        import logging
        logging.nodecanvas = self
        return bool(self._busy_stack)

    def push_busy(self, name):
        """Push a busy context name onto the busy stack

        :param name: name of busy context, used for debugging
        """
        self._busy_stack.append(name)

    def pop_busy(self, name):
        """Pop a busy context name from the busy stack

        :param name: name of busy context, used for debugging
        """
        assert self._busy_stack[-1] == name, name
        self._busy_stack[:] = self._busy_stack[:-1]

    def rename_blender_node(self, node, name, set_label=True):
        """Rename Blender node

        :param node: Blender node instance
        :param name: new name
        :param set_label: option to also set label
        """
        self.push_busy("rename")
        node.name = name

        if set_label:
            node.label = name

        self.pop_busy("rename")

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
        self.push_busy("_add")

        try:
            self._labels.append(name)
            node_tree = self.bntm.get_nodetree()

            node_class = self.get_nodeclass()
            node = node_tree.nodes.new(node_class.bl_idname)

            node.location = position
            node.set_attributes(attributes)
            node_tree.nodes.active = node
            self.rename_blender_node(node, id_)

        finally:
            self.pop_busy("_add")

    def on_copy_nodes(self, copied_nodes):
        """Blender callback when new nodes are detected

        :param copied_nodes: optionally use these nodes instead of reading new nodes from graph
        """
        if not copied_nodes:
            return

        # Stop external operations
        self.push_busy("on_copy")

        # Ensure no pending copy operations
        self.perform_pending_copy_operations()

        # Cleanup Blender nodes
        logging.debug("Found Blender copied nodes {}".format(copied_nodes.values()))
        nodetree = self.bntm.get_nodetree()
        for blender_node in copied_nodes.values():
            logging.debug("Duplicated Blender node was deleted {}, will be added by the clipboard"
                          .format(blender_node.name))
            nodetree.nodes.remove(blender_node)

        # Load in hivemap
        hivemap = self._hgui()._clipboard().get_clipboard_value()

        if hivemap is None:
            logging.debug("Clipboard was empty!".format(hivemap))

        else:
            logging.debug("Loading clipboard: {}".format(hivemap))

            self._hgui().paste_clipboard()
            logging.debug("Pasted clipboard")

        self.pop_busy("on_copy")

    def h_add_node(self, id_, hnode):
        """Create GUI node (from HGUI canvas

        :param id_: id of node
        :param hnode:
        """
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
        node = [n for n in nodetree.nodes if n.name == node.name][0]

        self.push_busy("morph")

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

            at0.name = [n for n in mapnode.attributes if n.name == attribute_name_b][0].label

        # Remove unmatched sockets
        # This should be safe: attributes with connections won't be allowed to be deleted
        change = True
        while change:
            change = False
            for antenna in node.inputs:
                if antenna.identifier not in matched_inputs:
                    node.inputs.remove(antenna)
                    change = True

        change = True
        while change:
            change = False
            for antenna in node.outputs:
                if antenna.identifier not in matched_outputs:
                    node.outputs.remove(antenna)
                    change = True

        #Create new sockets that didn't exist before
        for antenna in mapnode.attributes:
            label = antenna.name
            if antenna.label is not None:
                label = antenna.label

            if antenna.outhook:
                if antenna.name in accounted_outputs:
                    continue

                in_hook = antenna.outhook
                if antenna.inhook:
                    socket_type = NodeSocket.socketclasses[in_hook.shape, in_hook.color, True]  #complementary socket
                else:
                    socket_type = NodeSocket.socketclasses[in_hook.shape, in_hook.color]

                socket = node.outputs.new(socket_type.bl_idname, antenna.name)
                socket.name = label
                socket.link_limit = 99

            if antenna.inhook:
                if antenna.name in accounted_inputs:
                    continue

                in_hook = antenna.inhook
                socket_type = NodeSocket.socketclasses[in_hook.shape, in_hook.color]
                socket = node.inputs.new(socket_type.bl_idname, antenna.name)
                socket.name = label
                socket.link_limit = 99

        #Assign the correct rows
        inputs = iter(node.inputs)
        outputs = iter(node.outputs)

        for index, antenna in enumerate(mapnode.attributes):
            if antenna.inhook:
                socket = next(inputs)
                socket.row = index + 1

            if antenna.outhook:
                socket = next(outputs)
                socket.row = index + 1

        self.pop_busy("morph")

    def gui_moves_node(self, id_, position):
        ret = True
        if self._hgui is not None:
            ret = self._hgui().gui_moves_node(id_, unscalepos(position))
        return ret

    def select(self, ids):
        nodetree = self.bntm.get_nodetree()
        nodenames = [self._nodes[id].name for id in ids]
        for node in nodetree.nodes:
            if node.name in nodenames:
                node.select = True
            else:
                node.select = False

        if len(nodenames) == 1:
            nodename = nodenames[0]
            for node in nodetree.nodes:
                if node.name == nodename:
                    nodetree.nodes.active = node
                    break

    def is_pending_copy(self, blender_node):
        """Determine if a blender node is marked for copying

        :param blender_node: Blender node instance
        """
        return blender_node.name in self._pending_copy

    def mark_pending_copy(self, blender_node):
        """Store worker ID for pending copy

        :param blender_node: Blender node requesting copy
        """
        # Use Blender label this is called from a copy
        node_id = blender_node.label
        self._pending_copy.add(node_id)

        from .BlendManager import blendmanager
        blendmanager.schedule(self.perform_pending_copy_operations)

    def perform_pending_copy_operations(self):
        """Read the worker IDs from the copy buffer and perform a clipboard copy operation"""
        if not self._pending_copy:
            return

        try:
            self._hgui().copy_clipboard(self._pending_copy)

        except Exception:
            logging.exception("Couldn't write clipboard")

        else:
            hivemap = self._hgui()._clipboard().get_clipboard_value()
            logging.debug("Written clipboard: {}".format(hivemap))

        finally:
            self._pending_copy.clear()

    def remove_node(self, id_):
        self.push_busy("remove_node")
        if id_ in self._positions:
            self._positions.pop(id_)

        node = self._nodes.pop(id_)
        nodetree = self.bntm.get_nodetree()

        for nr, n in list(enumerate(nodetree.nodes)):
            if n.name != node.name:
                continue

            nodetree.nodes.remove(n)
            self._labels.pop(nr)
            break

        self._links = {FakeLink.from_link(l) for l in nodetree.links}
        self.pop_busy("remove_node")

    def rename_node(self, old_id, new_id, new_name):
        self.push_busy("rename")
        node = self._nodes.pop(old_id)
        self._nodes[new_id] = node
        old_name = node.name
        node.name = new_name
        nodetree = self.bntm.get_nodetree()

        for nr, n in enumerate(nodetree.nodes):
            if n.name != old_name:
                continue

            self.rename_blender_node(n, new_name)
            self._labels[nr] = new_name

            break

        if self._selection is not None and old_name in self._selection:
            pos = self._selection.pop(old_name)
            self._selection[new_name] = pos
            if self._hgui is not None:
                sel = [n for n in self._selection if self._selection[n]]
                selected_ids = [id_ for id_, n in self._nodes.items() if n.name in sel]
                #self._hgui().gui_selects(selected_ids)
        self.pop_busy("rename")

    def h_add_connection(self, id_, connection, valid):
        self.push_busy("h_add")
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

        # Adding a new link goes slowly ...
        fake_link_ = FakeLink.from_link(link)
        self._links.add(fake_link_)

        start.check_update()
        end.check_update()
        self.pop_busy("h_add")

    def gui_adds_connection(self, link, force):
        connection = self.map_link(link)
        con_id = next(self._connection_generator)
        success = True
        if self._hgui is not None:
            success = self._hgui().gui_adds_connection(connection, con_id, force)

        if success or force:
            self._connections[con_id] = connection
            link.use_socket_color = True
            link.dashed = (link.from_socket._shape == "DIAMOND")

        if force and not success:
            # connection.setColor(disallowed_connection_color) #TODO
            link.use_socket_color = False

        return success

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
        if not id_ in self._connections:
            logging.debug("no GUI connection found (maybe initial folding)")
            return

        self.push_busy("remove_con")
        tree = self.bntm.get_nodetree()
        connection = self._connections.pop(id_)

        for link in tree.links:
            c = self.map_link(link)
            if c == connection:
                tree.links.remove(link)

        self.pop_busy("remove_con")

    def set_statusbar_message(self, message):
        if self._statusbar is None:
            return
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
            if n.name != id_:
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
        for connection_id, connection_ in self._connections.items():
            print(connection_, connection)
            if connection_ == connection:
                return connection_id
        raise KeyError

    def map_link(self, link):
        from ..HGui import Connection

        start_node = link.from_node.label
        start_attribute = link.from_socket.identifier
        end_node = link.to_node.label
        end_attribute = link.to_socket.identifier
        return Connection(start_node, start_attribute, end_node, end_attribute, [], )
