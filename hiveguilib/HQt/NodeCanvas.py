from __future__ import print_function, absolute_import

import weakref

from ..HUtil.Node import Node, h_map_node

from . import HQt
from . import widgets
from .. import HGui

disallowed_connection_color = (150, 0, 0)


def find_attribute(nodename, nodeUi, attribute):
    at = [a for a in nodeUi._attributeUis if a._params.name == attribute]
    if len(at) == 0:
        raise NameError("NodeUi '%s' has no AttributeUi named '%s'" % (nodename, attribute))
    elif len(at) > 1:
        raise NameError("NodeUi '%s' has %d AttributeUis named '%s'" % (nodename, len(at), attribute))
    return at[0]


def new_connection():
    n = 0
    while 1:
        n += 1
        yield "connection-%d" % n


class NodeCanvas(HQt):
    _nodeUiClass = widgets.NodeUi
    _attributeUiClass = widgets.AttributeUi
    _hgui = None
    _connection_generator = new_connection()

    def __init__(self, mainWindow, clipboard, statusbar):
        self._nodeCanvas = widgets.NodeCanvas(mainWindow.qt())
        self._nodeCanvas._hqt = weakref.ref(self)
        self._scene = widgets.NodeUiScene()
        self._scene._hqt = weakref.ref(self)
        self._view = widgets.NodeView(self._nodeCanvas, clipboard)
        self._view.setScene(self._scene)
        self._statusbar = statusbar

        self._nodes = {}
        self._nodeuis = {}
        self._nodeuis_rev = {}
        self._connections = {}

    def _add_node(self, id_, name, attributes, position=None, tooltip=""):
        nodeUi = self._nodeUiClass(name, attributes, tooltip)

        if position is not None:
            nodeUi.setPos(*position)

        self._nodeuis[id_] = nodeUi
        self._nodeuis_rev[nodeUi] = id_
        self._scene.addItem(nodeUi)
        nodeUi.updateLayout()

    def _morph_node(self, id_, nodeUi, newnodeUi, mapcon):

        for atname0, atname1, mode in mapcon:
            at0 = find_attribute(id_ + ":old", nodeUi, atname0)
            at1 = find_attribute(id_ + ":new", newnodeUi, atname1)
            at1.setVisible(at0.isVisible())
            assert mode in ("in", "out")

            if mode == "in":
                at0in = at0._inputHook
                assert at0in is not None, atname0
                at1in = at1._inputHook
                assert at1in is not None, atname1
                for con in at0in._connections:
                    con.setEndHook(at1in)
            if mode == "out":
                at0out = at0._outputHook
                assert at0out is not None, atname0
                at1out = at1._outputHook
                assert at1out is not None, atname1
                for con in list(at0out._connections):
                    con.setStartHook(at1out)

        newnodeUi.updateLayout()

    def h_add_node(self, id_, hnode):
        node = h_map_node(hnode)
        pos = node.position[0], -node.position[1]
        self._add_node(id_, node.name, node.attributes, pos, node.tooltip)
        self._nodes[id_] = node

    def h_morph_node(self, id_, hnode, mapcon):
        newnode = h_map_node(hnode)
        pos = newnode.position[0], -newnode.position[1]
        newnodeUi = self._nodeUiClass(newnode.name, newnode.attributes, newnode.tooltip)
        newnodeUi.setPos(*pos)

        nodeUi = self._nodeuis[id_]
        self._nodeuis[id_] = newnodeUi
        self._nodeuis_rev.pop(nodeUi)
        self._nodeuis_rev[newnodeUi] = id_
        self._scene.addItem(newnodeUi)
        self._morph_node(id_, nodeUi, newnodeUi, mapcon)
        newnodeUi.updateLayout()
        nodeUi.deleteIt()
        self._hgui().select([id_])

    def select(self, ids):
        items = [self._nodeuis[id_] for id_ in ids]
        self._view.setSelectedItems(items)

    def gui_selects(self, nodeUiList):
        ids = [self._nodeuis_rev[nodeUi] for nodeUi in nodeUiList]
        ret = True
        if self._hgui is not None:
            ret = self._hgui().gui_selects(ids)
        return ret

    def gui_deselects(self):
        ret = True
        if self._hgui is not None:
            ret = self._hgui().gui_deselects()
        return ret

    def remove_node(self, id_):
        if not id_ in self._nodeuis:
            return

        nodeUi = self._nodeuis.pop(id_)
        self._nodeuis_rev.pop(nodeUi)
        nodeUi.deleteIt()

    def rename_node(self, old_id, new_id, new_name):
        assert old_id in self._nodeuis, old_id
        assert new_id not in self._nodeuis, new_id
        nodeUi = self._nodeuis.pop(old_id)
        self._nodeuis[new_id] = nodeUi
        self._nodeuis_rev[nodeUi] = new_id
        nodeUi.setName(new_name)
        node = self._nodes.pop(old_id)
        self._nodes[new_id] = node
        # connections do not need to be updated:
        #  they refer to the nodeUi, not to its ID (which HGui does)

    def gui_removes_nodes(self, nodeUis):
        ids = [self._nodeuis_rev[nodeUi] for nodeUi in nodeUis]
        ret = True
        if self._hgui is not None:
            ret = self._hgui().gui_removes_nodes(ids)
        return ret

    def gui_moves_node(self, nodeUi, offset):
        id_ = self._nodeuis_rev[nodeUi]
        node = self._nodes[id_]
        pos = nodeUi.scenePos()
        position = (pos.x(), -pos.y())

        ret = True
        if self._hgui is not None:
            ret = self._hgui().gui_moves_node(id_, position)
        if ret:
            node.position = position
            if self._hgui() is not None:
                offset = (offset.x(), -offset.y())
                for con_id, con in self._connections.items():
                    starthook = con.startHook()
                    if starthook is None: continue
                    startnodeUi = starthook._parentNodeUi()
                    if startnodeUi is nodeUi:
                        self._hgui().gui_offsets_connection_interpoints(con_id, offset)
        return ret

    def gui_asks_connection(self, connection, target):
        hconnection = self.map_connection(connection)
        target_node, target_hook = self.map_hook(target)
        hconnection.end_node, hconnection.end_attribute = target_node, target_hook
        ret = True
        if self._hgui is not None:
            ret = self._hgui().gui_asks_connection(hconnection)
        if not ret:
            connection.setColor(disallowed_connection_color)
        return ret

    def h_add_connection(self, id_, hconnection, valid):
        assert id_ not in self._connections, id_

        start_node = self._nodeuis[hconnection.start_node]
        start = find_attribute(hconnection.start_node, start_node,
                               hconnection.start_attribute)

        end_node = self._nodeuis[hconnection.end_node]
        end = find_attribute(hconnection.end_node, end_node,
                             hconnection.end_attribute)

        connection = widgets.Connection(start._outputHook, end._inputHook, id_)
        self._connections[id_] = connection
        connection.h_setInterpoints(hconnection.interpoints)
        if not valid:
            connection.setColor(disallowed_connection_color)
        connection.updatePath()

    def gui_adds_connection(self, connection, force):
        hconnection = self.map_connection(connection)
        con_id = next(self._connection_generator)
        connection.id = con_id
        ret = True
        if self._hgui is not None:
            ret = self._hgui().gui_adds_connection(hconnection, con_id, force)
        if ret or force:
            self._connections[con_id] = connection
        if force and not ret:
            connection.setColor(disallowed_connection_color)
        return ret

    def remove_connection(self, id_):
        # Shell meta instantiation has no actual connections
        if not id_ in self._connections:
            return
        connection = self._connections.pop(id_)
        connection.deleteIt()

    def gui_removes_connection(self, connection):
        if self._hgui is None: return True
        ret = self._hgui().gui_removes_connection(connection.id)
        if ret:
            self._connections.pop(connection.id)
        return ret

    def gui_rearranges_connection(self, connection, other_connection, pos):
        return self._hgui().gui_rearranges_connection(
            connection.id, other_connection.id, pos
        )

    def copy_clipboard(self, nodeUis):
        if self._hgui is None: return
        ids = [self._nodeuis_rev[nodeUi] for nodeUi in nodeUis]
        self._hgui().copy_clipboard(ids)

    def paste_clipboard(self):
        if self._hgui is None: return
        self._hgui().paste_clipboard()

    def set_statusbar_message(self, message):
        if self._statusbar is None: return
        self._statusbar.setMessage(message)

    def clear_statusbar_message(self):
        if self._statusbar is None: return
        self._statusbar.clearMessage()

    def map_hook(self, hook):
        attr = hook.parentAttributeUi()
        attrname = attr._params.name
        node = attr.parentNodeUi()
        nodeid = self._nodeuis_rev[node]
        return nodeid, attrname

    def map_connection(self, connection):
        from ..HGui import Connection

        starthook = connection.startHook()
        start_node, start_attribute = self.map_hook(starthook)
        endhook = connection.endHook()
        end_node, end_attribute = self.map_hook(endhook)
        s = self._nodeuis[start_node].scenePos()
        sx, sy = s.x(), s.y()
        interpoints = [(float(p.x() + sx), -float(p.y() + sy)) for p in connection._interpoints]
        ret = Connection(start_node, start_attribute,
                         end_node, end_attribute,
                         interpoints,
        )
        return ret

    def set_attribute_value(self, id_, attribute, value):
        # nodes themselves are not modified!
        nodeUi = self._nodeuis[id_]
        print(id_, attribute)
        attributeUi = nodeUi.getAttributeUi(attribute)
        attributeUi.setValue(str(value))
        nodeUi.updateLayout()


    def hide_attribute(self, id_, attribute):
        nodeUi = self._nodeuis[id_]
        attributeUi = nodeUi.getAttributeUi(attribute)
        attributeUi.setVisible(False)
        nodeUi.updateLayout()

    def show_attribute(self, id_, attribute):
        nodeUi = self._nodeuis[id_]
        attributeUi = nodeUi.getAttributeUi(attribute)
        attributeUi.setVisible(True)
        nodeUi.updateLayout()

    def qt_scene(self):
        return self._scene

    def qt_view(self):
        return self._view

    def qt(self):
        return self._nodeCanvas
