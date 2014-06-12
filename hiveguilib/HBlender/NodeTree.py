import bpy, bpy.types
import logging
from . import level


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
        ret = []
        bntm = BlendManager.blendmanager.get_nodetree_manager(self.name)
        canvas = bntm.canvas
        ids = [node.label for node in self.nodes]
        for id_ in canvas.h()._nodes:
            if id_ not in ids:
                ret.append(id_)
        if ret:
            ok = canvas.gui_removes_nodes(ret)
            assert ok
        return ret

    def _check_links(self, deletions):
        bntm = BlendManager.blendmanager.get_nodetree_manager(self.name)
        print(self.name, bntm, bntm.canvas.h())
        hcanvas = bntm.canvas.h()
        changed = False
        new_connections = []
        removed_connections = []
        blinks = {(l.from_node, l.from_socket, l.to_node, l.to_socket) for l in hcanvas._links}
        for l in list(self.links):
            pair = l.from_node, l.from_socket, l.to_node, l.to_socket
            if pair in blinks:
                continue
                # print("NEW-CONNECTION", pair)
            new_connections.append(l)

        clinks = {(l.from_node, l.from_socket, l.to_node, l.to_socket) for l in self.links}
        for l in hcanvas._links:
            pair = l.from_node, l.from_socket, l.to_node, l.to_socket
            if pair not in clinks:
                # print("REMOVED-CONNECTION", pair)
                removed_connections.append(l)

        changed_nodes = []
        for l in new_connections:
            ok = hcanvas.gui_adds_connection(l, False)
            if not ok:
                self.links.remove(l)
            else:
                changed_nodes.append(l.from_node)
                changed_nodes.append(l.to_node)

        for l in removed_connections:
            if l.from_node.identifier in deletions: continue
            if l.to_node.identifier in deletions: continue
            ok = hcanvas.gui_removes_connection(l)
            if not ok:
                logging.debug("removal of connection was disapproved, what to do?")
            else:
                changed_nodes.append(l.from_node)
                changed_nodes.append(l.to_node)

        for node in changed_nodes:
            node.check_update()

        hcanvas._links = {FakeLink.from_link(l) for l in self.links}

    def _check_positions(self):
        import copy

        bntm = BlendManager.blendmanager.get_nodetree_manager(self.name)
        canvas = bntm.canvas
        hcanvas = canvas.h()
        if hcanvas._positions is None:
            pos = {}
            for node in self.nodes:
                pos[node.label] = copy.copy(node.location)
            hcanvas._positions = pos
        else:
            pos = hcanvas._positions
            for node in self.nodes:
                l = node.label
                if l not in pos or pos[l] != node.location:
                    pos[l] = copy.copy(node.location)
                    hcanvas.gui_moves_node(l, pos[l])

    def _check_selection(self):
        bntm = BlendManager.blendmanager.get_nodetree_manager(self.name)
        canvas = bntm.canvas
        hcanvas = canvas.h()
        selected = []
        if hcanvas._selection is None:
            sel = {}
            for node in self.nodes:
                sel[node.label] = bool(node.select)
                if node.select: selected.append(node.label)
            hcanvas._selection = sel
            if selected: canvas.gui_selects(selected)
        else:
            changed = False
            sel = hcanvas._selection
            for node in self.nodes:
                l = node.label
                if l not in sel:
                    sel[l] = bool(node.select)
                    if sel[l]:
                        selected.append(l)
                        changed = True
                elif sel[l] != node.select:
                    if node.select:
                        selected.append(l)
                    changed = True
                    sel[l] = bool(node.select)
            if changed:
                if selected:
                    ok = canvas.gui_selects(selected)
                    assert ok
                else:
                    ok = canvas.gui_deselects()
                    assert ok
                if bpy.context.screen is not None:
                    for area in bpy.context.screen.areas:
                        space = area.spaces[0]
                        if space.type != 'NODE_EDITOR': continue
                        if space.edit_tree.name != self.name: continue
                        area.tag_redraw()


    def find_node(self, name):
        for node in self.nodes:
            if node.label == name: return node
        raise AttributeError(name)

    def update(self):
        if BlendManager.blendmanager._loading: return

        bntm = BlendManager.blendmanager.get_nodetree_manager(self.name)
        canvas = bntm.canvas
        hcanvas = canvas.h()
        if hcanvas._busy: return

        deletions = self._check_deletions()
        self._check_links(deletions)

    def full_update(self):
        """
        #We have been triggered from Node.draw_buttons, so we are in an unprivileged "draw" context
        #Therefore, don't do this stuff right away, but schedule it for the next scene update
        
        self._check_positions()
        self._check_selection()
        """
        BlendManager.blendmanager.schedule(self._check_positions)
        BlendManager.blendmanager.schedule(self._check_selection)


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
    from .BlendManager import blendmanager

    if context.space_data.tree_type == "Spydermap" and context.space_data.edit_tree is not None:
        blendmanager.spyderhive_widget.draw(context, self.layout)


def register():
    bpy.utils.register_class(HivemapNodeTree)
    bpy.utils.register_class(WorkermapNodeTree)
    bpy.utils.register_class(SpydermapNodeTree)
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


def unregister():
    bpy.utils.unregister_class(HivemapNodeTree)
    bpy.utils.unregister_class(WorkermapNodeTree)
    bpy.utils.unregister_class(SpydermapNodeTree)
    bpy.types.NODE_HT_header.remove(draw_hive_level)
    bpy.types.NODE_HT_header.remove(draw_use_hive)
    bpy.types.NODE_HT_header.remove(draw_spyderhive)

if __name__ == "__main__":
    unregister()
    register()