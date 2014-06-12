from __future__ import print_function, absolute_import

from . import HGui, Connection, Node, Hook, Attribute
import weakref
from bee.types import typecompare as bee_typecompare


def typecompare(t1, t2):
    if t1 == "any" or t2 == "any": return True
    return bee_typecompare(t1, t2)


class NodeCanvas(HGui):
    _NodeCanvasClass = None

    def __init__(self, mainWindow, clipboard, statusbar=None):
        assert self._NodeCanvasClass is not None
        self._hNodeCanvas = self._NodeCanvasClass(mainWindow.h(), clipboard, statusbar)
        mainWindow.setNodeCanvas(self)
        self.mainWindow = mainWindow
        self._hNodeCanvas._hgui = weakref.ref(self)

        self._connections = {}
        self._connection_ids = []
        self._nodes = {}
        self.observers_selection = []
        self.observers_remove = []
        self._clipboard = weakref.ref(clipboard)
        self.workermanager = None
        self._busy = False
        self._folded_antenna_variables = {}
        self._folded_antenna_connections = {}
        self._folded_antennas = {}

    def set_workermanager(self, workermanager):
        self.workermanager = workermanager

    def add_connection(self, id_, start, end, interpoints=[]):
        start_node, start_attribute = start
        end_node, end_attribute = end

        if self._redundant_connection(
                start_node, end_node,
                start_attribute, end_attribute
        ):
            return

        assert start_node in self._nodes, start_node
        assert end_node in self._nodes, end_node

        connection = Connection(
            start_node, start_attribute,
            end_node, end_attribute,
            interpoints
        )

        assert id_ not in self._connections
        self._connections[id_] = connection
        self._connection_ids.append(id_)

        if start_node in self._folded_antenna_variables or \
                        end_node in self._folded_antenna_variables:
            return
        valid, pushpull = self._valid_connection(connection)
        if pushpull: valid = False
        self._hNodeCanvas.h_add_connection(id_, connection, valid)

    def _redundant_connection(self,
                              start_node, end_node,
                              start_attribute, end_attribute
    ):
        for con in self._connections.values():
            if con.start_node != start_node: continue
            if con.end_node != end_node: continue
            if con.start_attribute != start_attribute: continue
            if con.end_attribute != end_attribute: continue
            return True
        return False

    def _valid_connection(self, connection):
        ret = False
        pushpull = False
        while 1:
            start_node = self._nodes[connection.start_node]
            start = start_node.get_attribute(connection.start_attribute)
            start = start.outhook
            if start is None: break

            end_node = self._nodes[connection.end_node]
            end = end_node.get_attribute(connection.end_attribute)
            end = end.inhook
            if end is None: break

            # unequal types
            if not typecompare(start.type, end.type): break
            # unequal modes: only allowed if pull=>push, and if popups supported
            if start.mode != end.mode:
                if start.mode != "pull": break
                if not self.mainWindow.supports_popup(): break
                pushpull = True

            #more than 1 connection to pull antenna
            if end.mode == "pull":
                first_con = True
                for con in self._connections.values():
                    if con is connection: continue
                    if con.end_node != connection.end_node: continue
                    if con.end_attribute != connection.end_attribute: continue
                    first_con = False
                    break
                if not first_con:
                    break

            ret = True
            break
        if not ret: pushpull = False
        return ret, pushpull

    def gui_asks_connection(self, connection, adding=False):
        start_node, end_node = connection.start_node, connection.end_node
        start_attribute, end_attribute = connection.start_attribute, \
                                         connection.end_attribute

        if self._redundant_connection(
                start_node, end_node,
                start_attribute, end_attribute
        ):
            return False

        ok, pushpull = self._valid_connection(connection)
        if not pushpull or not adding: return ok
        if self.workermanager is None: return False  # in case we are running WorkerGUI

        result = self.mainWindow.popup("Poll mode", ["Manual", "Every tick", "On change"])
        if result is None: return False  # non-blocking popup
        self.pushpull_connection(connection, result)  # or: blocking popup
        return False  # in any case, the old connection must go

    def pushpull_connection(self, connection, pollmode):
        start_node = self._nodes[connection.start_node]
        end_node = self._nodes[connection.end_node]
        pos1 = start_node.position
        pos2 = end_node.position
        midpos = (pos1[0] + pos2[0]) / 2, (pos1[1] + pos2[1]) / 2
        if pollmode == "Manual":
            transistor = "dragonfly.std.transistor"
            t_offy = 0
            trigger = None
        elif pollmode == "Every tick":
            transistor = "dragonfly.std.transistor"
            trigger = "dragonfly.io.ticksensor"
            t_offy = 50
        elif pollmode == "On change":
            transistor = "dragonfly.std.sync"
            t_offy = 0
            trigger = None
        else:
            raise ValueError(pollmode)

        transistor_id = self.workermanager.get_new_workerid(transistor)
        start = start_node.get_attribute(connection.start_attribute)
        metaparams = {"type": start.outhook.type}
        t = self.workermanager.instantiate(
            transistor_id, transistor, midpos[0], midpos[1] + t_offy, metaparams
        )
        self.add_connection(
            self.workermanager.get_new_connection_id("con"),
            (connection.start_node, connection.start_attribute),
            (transistor_id, "inp"),
        )
        self.add_connection(
            self.workermanager.get_new_connection_id("con"),
            (transistor_id, "outp"),
            (connection.end_node, connection.end_attribute),
        )
        if trigger is not None:
            trigger_id = self.workermanager.get_new_workerid(trigger)
            tr = self.workermanager.instantiate(
                trigger_id, trigger, midpos[0] - 100, midpos[1] - 50
            )
            self.add_connection(
                self.workermanager.get_new_connection_id("con"),
                (trigger_id, "outp"),
                (transistor_id, "trig"),
            )

    def gui_adds_connection(self, connection, id_, force=False):
        ret = self.gui_asks_connection(connection, adding=True)
        if ret or force:
            assert id_ not in self._connections
            self._connections[id_] = connection
            self._connection_ids.append(id_)
        return ret

    def gui_offsets_connection_interpoints(self, con_id, offset):
        if self._busy: return
        con = self._connections[con_id]
        dx, dy = offset
        con.interpoints = [(x + dx, y + dy) for x, y in con.interpoints]

    def gui_rearranges_connection(self, con_id, insertionpoint, pos):
        if self._busy: return
        assert pos in ("before", "after"), pos
        old_index = self._connection_ids.index(con_id)
        new_index = self._connection_ids.index(insertionpoint)
        if old_index < new_index: new_index -= 1
        if pos == "after": new_index += 1
        if old_index == new_index: return True
        self._connection_ids.pop(old_index)  # removes con_id
        if new_index == len(self._connections):
            self._connection_ids.append(con_id)
        else:
            self._connection_ids.insert(new_index, con_id)
        return True

    def remove_connection(self, id_, pass_downward=True):
        self._connections.pop(id_)
        self._connection_ids.remove(id_)
        if id_ in self._folded_antenna_connections.values():
            for k, v in self._folded_antenna_connections.items():
                if v == id_:
                    self._folded_antenna_connections.pop(k)
                    break
        elif pass_downward:
            self._hNodeCanvas.remove_connection(id_)

    def gui_removes_connection(self, id_):
        if self._busy: return False
        if id_ in self._folded_antenna_connections.values(): return False
        self._connections.pop(id_)
        self._connection_ids.remove(id_)
        return True

    def add_node(self, id_, node):
        assert isinstance(node, Node)
        assert id_ not in self._nodes, id_
        assert id_ not in self._folded_antenna_variables, id_
        self._nodes[id_] = node
        self._hNodeCanvas.h_add_node(id_, node)

    def get_node(self, id_):
        return self._nodes[id_]

    def rename_node(self, old_id, new_id, new_name):
        assert old_id in self._nodes, old_id
        assert new_id not in self._nodes, new_id
        node = self._nodes.pop(old_id)
        node.name = new_name
        self._nodes[new_id] = node
        for con in self._connections.values():
            if con.start_node == old_id: con.start_node = new_id
            if con.end_node == old_id: con.end_node = new_id
        if old_id in self._folded_antenna_variables:
            folding_node, folding_antenna = self._folded_antenna_variables.pop(old_id)
            self._folded_antennas[folding_node][folding_antenna] = new_id
            self._folded_antenna_variables[new_id] = folding_node, folding_antenna
            con_id = self._folded_antenna_connections.pop(old_id)
            self._folded_antenna_connections[new_id] = con_id
        else:
            if old_id in self._folded_antennas:
                antennas = self._folded_antennas.pop(old_id)
                self._folded_antennas[new_id] = old_id
            self._hNodeCanvas.rename_node(old_id, new_id, new_name)
        self._busy = True
        self.select([new_id])
        self._busy = False

    def morph_node(self, id_, newnode, maps_in, maps_out):
        assert id_ in self._nodes, id_
        mapcon = []
        for conid in self._connection_ids:
            con = self._connections[conid]
            if con.start_node == id_:
                a = con.start_attribute
                if maps_out is not None:
                    aa = maps_out[a]
                    if aa is None: raise KeyError
                else:
                    aa = a
                con.start_attribute = aa
                mapcon.append((a, aa, "out"))
            if con.end_node == id_:
                a = con.end_attribute
                if maps_in is not None:
                    aa = maps_in[a]
                    if aa is None: raise KeyError
                else:
                    aa = a
                con.end_attribute = aa
                mapcon.append((a, aa, "in"))
        self._nodes[id_] = newnode
        if id_ not in self._folded_antenna_variables:
            self._hNodeCanvas.h_morph_node(id_, newnode, mapcon)

    def copy_clipboard(self, nodes):
        self._clipboard().nodecanvas_copy_nodes(nodes)

    def paste_clipboard(self):
        ids = self._clipboard().nodecanvas_paste_nodes()
        if ids is not None: self.select(ids)

    def select(self, ids):
        for id_ in ids:
            assert id_ in self._nodes, id_
            assert id_ not in self._folded_antenna_variables, id_
        self._hNodeCanvas.select(ids)

    def gui_selects(self, ids):
        if self._busy: return
        for ob in self.observers_selection:
            ob(ids)
        return True

    def gui_deselects(self):
        if self._busy: return
        for ob in self.observers_selection:
            ob(None)
        return True

    def gui_adds_node(self, id_, node):
        if self._busy: return
        assert isinstance(node, Node)
        assert id_ not in self._nodes
        self._nodes[id_] = node
        return True

    def _remove_node(self, id_, pass_downward=True):
        assert id_ in self._nodes, id_
        self._nodes.pop(id_)
        for con_id, connection in list(self._connections.items()):
            if connection.start_node == id_ or \
                            connection.end_node == id_:
                self.remove_connection(con_id, pass_downward)
        if id_ in self._folded_antennas:
            antennas = self._folded_antennas.pop(id_)
            for vid in antennas.values():
                self._folded_antenna_variables.pop(vid)
                self._remove_node(vid, pass_downward=False)
                for ob in self.observers_remove:
                    ob(vid)

    def remove_node(self, id_):
        self._remove_node(id_)
        assert id_ not in self._folded_antenna_variables, id_
        self._hNodeCanvas.remove_node(id_)

    def gui_removes_nodes(self, ids):
        if self._busy: return
        for id_ in ids:
            if id_ in self._folded_antenna_variables: continue
            self._remove_node(id_)
            for ob in self.observers_remove:
                ob(id_)
        return True

    def gui_moves_node(self, id_, position):
        if self._busy: return
        node = self._nodes[id_]
        node.position = position
        return True

    def get_connections(self):
        return [self._connections[id_] for id_ in self._connection_ids]

    def get_connection_ids(self):
        return self._connection_ids

    def set_attribute_value(self, id_, attribute, value):
        if id_ in self._folded_antenna_variables: return
        # nodes themselves are not modified!
        self._hNodeCanvas.set_attribute_value(id_, attribute, value)

    def fold_antenna_connection(self, id_, antenna, typ, onload):
        assert id_ in self._nodes, id_
        assert id_ not in self._folded_antenna_variables, id_
        if id_ in self._folded_antennas:
            assert antenna not in self._folded_antennas[id_], (id_, antenna)

        foldable = True
        varid = None
        value = None
        con_id = None
        for conid in self._connection_ids:
            con = self._connections[conid]
            if con.end_node == id_ and con.end_attribute == antenna:
                varid = con.start_node
                foldable = False
                desc = self.workermanager.get_worker_descriptor(varid)
                gp = desc[7].get("guiparams", {})
                if not onload:
                    coor_ok = True
                else:
                    coor_ok = False
                    x, y = desc[2], desc[3]
                    if x == 0 and y == 0: coor_ok = True
                if "is_variable" in gp and gp["is_variable"] and coor_ok:
                    vcon = [c for c in self._connections.values() \
                            if c.start_node == varid or c.end_node == varid]
                    vartype = desc[4]["type"]
                    if len(vcon) == 1 and vartype == typ:
                        foldable = True
                        con_id = conid
                        self._nodes[varid].position = 0, 0
                        if isinstance(desc[5], dict) and "value" in desc[5]:
                            value = desc[5]["value"]
                break

        if not foldable or (varid is None and onload):
            return False, None

        if varid is None:
            varid = id_.rstrip("_") + "_ant_" + antenna
            varid0 = varid
            count = 0
            while varid in self._nodes:
                count += 1
                varid = varid0 + str(count)
            metaparamvalues = {"type": typ}
            self.workermanager.instantiate(
                varid, "dragonfly.std.variable", 0, 0,
                metaparamvalues=metaparamvalues,
            )
            con_id = self.workermanager.get_new_connection_id("con")
            wim = self.workermanager.get_wim()
            wim.add_connection(con_id, (varid, "outp"), (id_, antenna))

        if id_ not in self._folded_antennas:
            self._folded_antennas[id_] = {}
        self._folded_antennas[id_][antenna] = varid
        self._folded_antenna_variables[varid] = id_
        self._folded_antenna_connections[varid] = con_id

        # remove the folded node from the rendered canvas
        self._hNodeCanvas.remove_connection(con_id)
        self._hNodeCanvas.remove_node(varid)
        self._hNodeCanvas.hide_attribute(id_, antenna)

        self.select([id_])
        return True, value

    def get_antenna_connected_variable(self, workerid, antenna):
        assert workerid in self._folded_antennas, workerid
        assert antenna in self._folded_antennas[workerid], antenna
        return self._folded_antennas[workerid][antenna]

    def expand_antenna_connection(self, workerid, antenna):
        varid = self.get_antenna_connected_variable(workerid, antenna)
        node = self._nodes[workerid]
        for anr in range(len(node.attributes)):
            a = node.attributes[anr]
            if a.name == antenna: break
        yrange = (anr + 0.5) / len(node.attributes) - 0.5
        x = node.position[0] - 150
        y = node.position[1] - 50 - 300 * yrange
        variable = self._nodes[varid]
        variable.position = x, y
        self._hNodeCanvas.h_add_node(varid, variable)
        con_id = self._folded_antenna_connections[varid]
        connection = self._connections[con_id]
        valid, pushpull = self._valid_connection(connection)
        if pushpull: valid = False
        self._hNodeCanvas.show_attribute(workerid, antenna)
        self._hNodeCanvas.h_add_connection(con_id, connection, valid)

        self._folded_antennas[workerid].pop(antenna)
        self._folded_antenna_variables.pop(varid)
        self._folded_antenna_connections.pop(varid)
        desc = self.workermanager.get_worker_descriptor(varid)
        if isinstance(desc[5], dict) and "value" in desc[5]:
            value = desc[5]["value"]
            self._hNodeCanvas.set_attribute_value(varid, "value", value)
        self.select([workerid])

    def h(self):
        return self._hNodeCanvas
  
