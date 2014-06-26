from __future__ import print_function, absolute_import

from . import HGui, Connection, Node, Hook, Attribute
import weakref
from bee.types import typecompare as bee_typecompare


def compare_types(type_a, type_b):
    if type_a == "any" or type_b == "any":
        return True

    return bee_typecompare(type_a, type_b)


class NodeCanvas(HGui):
    _NodeCanvasClass = None

    def __init__(self, main_window, clipboard, status_bar=None):
        assert self._NodeCanvasClass is not None
        self._hNodeCanvas = self._NodeCanvasClass(main_window.h(), clipboard, status_bar)
        main_window.setNodeCanvas(self)
        self.mainWindow = main_window

        self._busy = False
        self._clipboard = weakref.ref(clipboard)
        self._connections = {}
        self._connection_ids = []
        self._folded_antenna_variables = {}
        self._folded_antenna_connections = {}
        self._folded_antennas = {}
        self._hNodeCanvas._hgui = weakref.ref(self)
        self._nodes = {}

        self.observers_selection = []
        self.observers_remove = []
        self.workermanager = None

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

        if start_node in self._folded_antenna_variables or end_node in self._folded_antenna_variables:
            return

        valid, pushpull = self._valid_connection(connection)

        if pushpull:
            valid = False

        self._hNodeCanvas.h_add_connection(id_, connection, valid)

    def _redundant_connection(self, start_node, end_node, start_attribute, end_attribute):
        """Determine if a connection with the given parameters already exists

        :param start_node: start node of connection
        :param end_node: end node of connection
        :param start_node: start attribute of connection
        :param end_attribute: end attribute of connection
        """
        for connection in self._connections.values():
            if connection.start_node != start_node:
                continue

            if connection.end_node != end_node:
                continue

            if connection.start_attribute != start_attribute:
                continue

            if connection.end_attribute != end_attribute:
                continue

            return True

        return False

    def _valid_connection(self, connection):
        """Determine if a connection is valid

        :param connection: connection instance
        :returns: is_valid boolean, is_push_pull boolean
        """
        is_valid = False
        push_pull = False

        while True:
            start_node = self._nodes[connection.start_node]
            start_attribute = start_node.get_attribute(connection.start_attribute)
            start_hook = start_attribute.outhook
            if start_hook is None:
                break

            end_node = self._nodes[connection.end_node]
            end_attribute = end_node.get_attribute(connection.end_attribute)
            end_hook = end_attribute.inhook
            if end_hook is None:
                break

            # unequal types
            if not compare_types(start_hook.type, end_hook.type):
                break

            # unequal modes: only allowed if pull=>push, and if popups supported
            if start_hook.mode != end_hook.mode:
                if start_hook.mode != "pull":
                    break

                if not self.mainWindow.supports_popup():
                    break

                push_pull = True

            #more than 1 connection to pull antenna
            if end_hook.mode == "pull":
                is_single_connection = True
                for connection in self._connections.values():
                    if connection is connection:
                        continue

                    if connection.end_node != connection.end_node:
                        continue

                    if connection.end_attribute != connection.end_attribute:
                        continue

                    is_single_connection = False
                    break

                if not is_single_connection:
                    break

            is_valid = True
            break

        if not is_valid:
            push_pull = False

        return is_valid, push_pull

    def gui_asks_connection(self, connection, adding=False):
        start_node, end_node = connection.start_node, connection.end_node
        start_attribute, end_attribute = connection.start_attribute, connection.end_attribute

        if self._redundant_connection(start_node, end_node, start_attribute, end_attribute):
            return False

        is_valid, is_push_pull = self._valid_connection(connection)
        if not is_push_pull or not adding:
            return is_valid

        if self.workermanager is None:
            return False  # in case we are running WorkerGUI

        result = self.mainWindow.popup("Poll mode", ["Manual", "Every tick", "On change"])
        if result is None:
            return False  # non-blocking popup

        self.pushpull_connection(connection, result)  # or: blocking popup
        return False  # in any case, the old connection must go

    def pushpull_connection(self, connection, pollmode):
        start_node = self._nodes[connection.start_node]
        end_node = self._nodes[connection.end_node]

        start_point = start_node.position
        end_point = end_node.position

        position_midpoint = (start_point[0] + end_point[0]) / 2, (start_point[1] + end_point[1]) / 2

        if pollmode == "Manual":
            transistor_type = "dragonfly.std.transistor"
            offset_y = 0
            trigger_type = None

        elif pollmode == "Every tick":
            transistor_type = "dragonfly.std.transistor"
            trigger_type = "dragonfly.io.ticksensor"
            offset_y = 50

        elif pollmode == "On change":
            transistor_type = "dragonfly.std.sync"
            offset_y = 0
            trigger_type = None

        else:
            raise ValueError(pollmode)

        transistor_id = self.workermanager.get_new_workerid(transistor_type)
        start = start_node.get_attribute(connection.start_attribute)
        metaparams = {"type": start.outhook.type}
        transistor = self.workermanager.instantiate(transistor_id, transistor_type, position_midpoint[0],
                                                    position_midpoint[1] + offset_y, metaparams)

        connection_id = self.workermanager.get_new_connection_id("con")
        self.add_connection(connection_id, (connection.start_node, connection.start_attribute), (transistor_id, "inp"))

        connection_id = self.workermanager.get_new_connection_id("con")
        self.add_connection(connection_id, (transistor_id, "outp"), (connection.end_node, connection.end_attribute))

        if trigger_type is None:
            return

        trigger_id = self.workermanager.get_new_workerid(trigger_type)
        trigger = self.workermanager.instantiate(trigger_id, trigger_type, position_midpoint[0] - 100,
                                                 position_midpoint[1] - 50)

        connection_id = self.workermanager.get_new_connection_id("con")
        self.add_connection(connection_id, (trigger_id, "outp"), (transistor_id, "trig"))

    def gui_adds_connection(self, connection, connection_id, force=False):
        has_permission = self.gui_asks_connection(connection, adding=True)
        if has_permission or force:
            assert connection_id not in self._connections
            self._connections[connection_id] = connection
            self._connection_ids.append(connection_id)
        return has_permission

    def gui_offsets_connection_interpoints(self, connection_id, offset):
        if self._busy:
            return

        connection_id = self._connections[connection_id]
        x_delta, y_delta = offset
        connection_id.interpoints = [(x + x_delta, y + y_delta) for x, y in connection_id.interpoints]

    def gui_rearranges_connection(self, connection_id, insertion_point, position):
        if self._busy:
            return

        assert position in ("before", "after"), position
        old_index = self._connection_ids.index(connection_id)
        new_index = self._connection_ids.index(insertion_point)

        if old_index < new_index:
            new_index -= 1

        if position == "after":
            new_index += 1

        if old_index == new_index:
            return True

        self._connection_ids.pop(old_index)  # removes con_id
        if new_index == len(self._connections):
            self._connection_ids.append(connection_id)

        else:
            self._connection_ids.insert(new_index, connection_id)

        return True

    def remove_connection(self, connection_id, pass_downward=True):
        self._connections.pop(connection_id)
        self._connection_ids.remove(connection_id)

        if connection_id in self._folded_antenna_connections.values():

            for connection, connection_id in self._folded_antenna_connections.items():

                if connection_id == connection_id:
                    self._folded_antenna_connections.pop(connection)
                    break

        elif pass_downward:
            self._hNodeCanvas.remove_connection(connection_id)

    def gui_removes_connection(self, connection_id):
        if self._busy:
            return False

        if connection_id in self._folded_antenna_connections.values():
            return False

        self._connections.pop(connection_id)
        self._connection_ids.remove(connection_id)
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

        for connection in self._connections.values():
            if connection.start_node == old_id:
                connection.start_node = new_id

            if connection.end_node == old_id:
                connection.end_node = new_id

        if old_id in self._folded_antenna_variables:
            folding_node, folding_antenna = self._folded_antenna_variables.pop(old_id)
            self._folded_antennas[folding_node][folding_antenna] = new_id
            self._folded_antenna_variables[new_id] = folding_node, folding_antenna
            connection_id = self._folded_antenna_connections.pop(old_id)
            self._folded_antenna_connections[new_id] = connection_id

        else:
            if old_id in self._folded_antennas:
                antennas = self._folded_antennas.pop(old_id)
                self._folded_antennas[new_id] = old_id

            self._hNodeCanvas.rename_node(old_id, new_id, new_name)

        self._busy = True
        self.select([new_id])
        self._busy = False

    def morph_node(self, node_id, replacement_node, maps_in, maps_out):
        assert node_id in self._nodes, node_id
        connection_map = []

        for connection_id in self._connection_ids:
            connection = self._connections[connection_id]
            if connection.start_node == node_id:
                start_attribute = connection.start_attribute

                if maps_out is not None:
                    aa = maps_out[start_attribute]
                    if aa is None:
                        raise KeyError

                else:
                    aa = start_attribute

                connection.start_attribute = aa
                connection_map.append((start_attribute, aa, "out"))

            if connection.end_node == node_id:
                start_attribute = connection.end_attribute
                if maps_in is not None:
                    aa = maps_in[start_attribute]

                    if aa is None:
                        raise KeyError

                else:
                    aa = start_attribute

                connection.end_attribute = aa
                connection_map.append((start_attribute, aa, "in"))

        self._nodes[node_id] = replacement_node
        if node_id not in self._folded_antenna_variables:
            self._hNodeCanvas.h_morph_node(node_id, replacement_node, connection_map)

    def copy_clipboard(self, node_ids):
        self._clipboard().nodecanvas_copy_nodes(node_ids)

    def paste_clipboard(self, pre_conversion=None):
        pasted_nodes_id_sequence = self._clipboard().nodecanvas_paste_nodes(pre_conversion)

        if pasted_nodes_id_sequence is None:
            return

        self.select(pasted_nodes_id_sequence)

    def select(self, selected_node_id_sequence):
        for node_id in selected_node_id_sequence:
            assert node_id in self._nodes, node_id
            assert node_id not in self._folded_antenna_variables, node_id
        self._hNodeCanvas.select(selected_node_id_sequence)

    def gui_selects(self, node_id_sequence):
        if self._busy:
            return

        for ob in self.observers_selection:
            ob(node_id_sequence)
        return True

    def gui_deselects(self):
        if self._busy:
            return

        for ob in self.observers_selection:
            ob(None)

        return True

    def gui_adds_node(self, id_, node):
        if self._busy:
            return

        assert isinstance(node, Node)
        assert id_ not in self._nodes
        self._nodes[id_] = node
        return True

    def _remove_node(self, node_id, pass_downward=True):
        assert node_id in self._nodes, node_id
        import logging
        logging.debug("RUNNING REMOVE" + node_id)
        if node_id in self._hNodeCanvas._nodes:
            self._hNodeCanvas.remove_node(node_id)
        self._nodes.pop(node_id)

        for connection_id, connection in list(self._connections.items()):
            if connection.start_node == node_id or connection.end_node == node_id:
                self.remove_connection(connection_id, pass_downward)

        if node_id in self._folded_antennas:
            antennas = self._folded_antennas.pop(node_id)
            for folded_node_id in antennas.values():
                self._folded_antenna_variables.pop(folded_node_id)
                self._remove_node(folded_node_id, pass_downward=False)

                for observer in self.observers_remove:
                    observer(folded_node_id)

    def remove_node(self, node_id):
        assert node_id not in self._folded_antenna_variables, node_id
        self._remove_node(node_id)

    def gui_removes_nodes(self, node_id_sequence):
        if self._busy:
            import logging
            logging.debug("BUSY, COULD NOT REMOVE")
            return

        for node_id in node_id_sequence:
            if node_id in self._folded_antenna_variables:
                continue
            import logging
            logging.debug(str(self) + "CALLING REMOVE FROM GUI_REMOVES_NODES" + node_id)

            self._remove_node(node_id)

            for ob in self.observers_remove:
                ob(node_id)

        return True

    def gui_moves_node(self, node_id, position):
        if self._busy: return
        node = self._nodes[node_id]
        node.position = position
        return True

    def get_connections(self):
        return [self._connections[node_id] for node_id in self._connection_ids]

    def get_connection_ids(self):
        return self._connection_ids

    def set_attribute_value(self, node_id, attribute, value):
        if node_id in self._folded_antenna_variables: return
        # nodes themselves are not modified!
        self._hNodeCanvas.set_attribute_value(node_id, attribute, value)

    def fold_antenna_connection(self, node_id, antenna, value_type, called_on_load):
        assert node_id in self._nodes, node_id
        assert node_id not in self._folded_antenna_variables, node_id
        if node_id in self._folded_antennas:
            assert antenna not in self._folded_antennas[node_id], (node_id, antenna)

        can_be_folded = True
        variable_id = None
        value = None
        connection_id = None
        for connection_id_ in self._connection_ids:
            connection = self._connections[connection_id_]
            if not (connection.end_node == node_id and connection.end_attribute == antenna):
                continue

            variable_id = connection.start_node
            can_be_folded = False
            worker_descriptor = self.workermanager.get_worker_descriptor(variable_id)
            gui_params = worker_descriptor[7].get("guiparams", {})

            if not called_on_load:
                coordinate_valid = True

            else:
                coordinate_valid = False
                x, y = worker_descriptor[2], worker_descriptor[3]
                if x == y == 0:
                    coordinate_valid = True

            if gui_params.get("is_variable") and coordinate_valid:
                variable_node = self._nodes[variable_id]
                variable_connections = [c for c in self._connections.values() if c.start_node == variable_id or
                                        c.end_node == variable_id]

                variable_type = worker_descriptor[4]["type"]
                if len(variable_connections) == 1 and variable_type == value_type:
                    can_be_folded = True
                    connection_id = connection_id_

                    if isinstance(worker_descriptor[5], dict) and "value" in worker_descriptor[5]:
                        value = worker_descriptor[5]["value"]

                    variable_node.position = 0, 0
            break

        if not can_be_folded or (variable_id is None and called_on_load):
            return False, None

        if variable_id is None:
            variable_id = node_id.rstrip("_") + "_ant_" + antenna
            original_variable_id = variable_id
            count = 0
            while variable_id in self._nodes:
                count += 1
                variable_id = original_variable_id + str(count)

            meta_params = {"type": value_type}
            self.workermanager.instantiate(variable_id, "dragonfly.std.variable", 0, 0, metaparamvalues=meta_params)
            connection_id = self.workermanager.get_new_connection_id("con")
            wim = self.workermanager.get_wim()
            wim.add_connection(connection_id, (variable_id, "outp"), (node_id, antenna))

        if node_id not in self._folded_antennas:
            self._folded_antennas[node_id] = {}

        self._folded_antennas[node_id][antenna] = variable_id
        self._folded_antenna_variables[variable_id] = node_id
        self._folded_antenna_connections[variable_id] = connection_id

        # remove the folded node from the rendered canvas
        self._hNodeCanvas.remove_connection(connection_id)
        self._hNodeCanvas.remove_node(variable_id)
        self._hNodeCanvas.hide_attribute(node_id, antenna)

        self.select([node_id])
        return True, value

    def get_antenna_connected_variable(self, worker_id, antenna):
        assert worker_id in self._folded_antennas, worker_id
        assert antenna in self._folded_antennas[worker_id], antenna
        return self._folded_antennas[worker_id][antenna]

    def expand_antenna_connection(self, worker_id, antenna):
        variable_id = self.get_antenna_connected_variable(worker_id, antenna)

        node = self._nodes[worker_id]
        variable = self._nodes[variable_id]

        # Get the attribute with the antenna name
        for index, attribute in enumerate(node.attributes):
            if attribute.name == antenna:
                break

        yrange = (index + 0.5) / len(node.attributes) - 0.5
        x = node.position[0] - 150
        y = node.position[1] - 50 - 300 * yrange

        variable.position = x, y
        self._hNodeCanvas.h_add_node(variable_id, variable)

        connection_id = self._folded_antenna_connections[variable_id]
        connection = self._connections[connection_id]
        valid, is_push_pull = self._valid_connection(connection)

        if is_push_pull:
            valid = False

        self._hNodeCanvas.show_attribute(worker_id, antenna)
        self._hNodeCanvas.h_add_connection(connection_id, connection, valid)

        self._folded_antennas[worker_id].pop(antenna)
        self._folded_antenna_variables.pop(variable_id)
        self._folded_antenna_connections.pop(variable_id)

        worker_descriptor = self.workermanager.get_worker_descriptor(variable_id)
        if isinstance(worker_descriptor[5], dict) and "value" in worker_descriptor[5]:
            value = worker_descriptor[5]["value"]
            self._hNodeCanvas.set_attribute_value(variable_id, "value", value)

        self.select([worker_id])

    def h(self):
        return self._hNodeCanvas

