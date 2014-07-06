import bpy
from . import scalepos, unscalepos, level


class AddHiveNode(bpy.types.Operator):
    bl_idname = "node.add_hive_node"
    bl_label = "Add a Hive system node to the Node Editor"

    type = bpy.props.StringProperty()

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            region = context.region
            x, y = event.mouse_region_x - (region.width / 2), event.mouse_region_y - (region.height / 2)
            node = context.active_node
            if node is None:
                return {'FINISHED'}

            node.location = x, y

        elif event.type == 'LEFTMOUSE':
            return {'FINISHED'}

        elif event.type == 'RIGHTMOUSE':
            context.active_node.location = 0, 0
            return {'FINISHED'}

        elif event.type == 'ESC':
            nodetree = context.space_data.edit_tree
            node = context.active_node
            nodetree.nodes.remove(node)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        # In Qt, dragged widgets generate their own events
        #In Blender, we have to contact the clipboard directly
        from . import BlendManager

        nodetree_name = context.space_data.edit_tree.name

        add_node = bpy.types.NODE_OT_add_node
        add_node.store_mouse_cursor(context, event)

        x, y = unscalepos(context.space_data.cursor_location)

        blend_node_tree_manager = BlendManager.blendmanager.blend_nodetree_managers[nodetree_name]
        pwc = blend_node_tree_manager.pwc
        pwc._select_worker(tuple(self.type.split(".")))
        clip = blend_node_tree_manager.clipboard
        clip.drop_worker(x, y)

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


bpy.utils.register_class(AddHiveNode)


class NodeItem:
    """FAKE DESC"""

    def __init__(self, manager, key, fullkey):
        self.manager = manager
        self.key = key
        self.fullkey = fullkey

    def _active(self, context):
        if context.space_data.edit_tree is None:
            return False

        if context.space_data.edit_tree.name not in self.manager._nodeitem_trees[self.fullkey]:
            return False
        if not level.active(context, tuple(self.fullkey.split("."))): return
        return True

    def draw(self, layout, context):
        default_context = bpy.app.translations.contexts.default
        props = layout.operator("node.add_hive_node", text=self.key, text_ctxt=default_context)
        props.type = self.fullkey


class NodeItemMenu:
    name = "NODE_MT_HIVE"

    def __init__(self, title, fullname, make_panel=False):
        if title is not None:
            assert fullname is not None

        self.title = title
        self.fullname = fullname
        self.children = []

        def menudraw(struct, context):
            if not level.active(context, self.fullname):
                return

            return self.draw(struct.layout, context)

        cls_dict = dict(bl_space_type='NODE_EDITOR', bl_label="<HiveMenu>", draw=menudraw, poll=self.poll)

        name = self.name
        if self.fullname is not None:
            name = self.name + "_" + "_".join(self.fullname)

        self.name = name
        self.menuclass = type(name, (bpy.types.Menu,), cls_dict)

        if make_panel:
            type_name = name.replace("NODE_MT_", "NODE_PT_")
            cls_dict = dict(bl_space_type='NODE_EDITOR', bl_label=title, bl_region_type='TOOLS',
                            bl_options={'DEFAULT_CLOSED'}, poll=self._active, draw=menudraw)
            self.panelclass = type(type_name, (bpy.types.Panel,), cls_dict)

        else:
            self.panelclass = None

    def register(self):
        if self.panelclass is not None:
            bpy.utils.register_class(self.panelclass)
        bpy.utils.register_class(self.menuclass)

    def unregister(self):
        if self.panelclass is not None:
            bpy.utils.unregister_class(self.panelclass)
        bpy.utils.unregister_class(self.menuclass)

    def _active(self, context):
        if not level.active(context, self.fullname):
            return False

        for child in self.children:
            if child._active(context):
                return True

        return False

    def draw(self, layout, context):
        col = layout.column()
        for child in self.children:
            if not child._active(context):
                continue

            if isinstance(child, NodeItemMenu):
                layout.menu(self.name + "_" + child.title, text=child.title)

            else:
                child.draw(col, context)

    @classmethod
    def poll(menucls, context):
        return False


class NodeItemManager:

    def __init__(self):
        self._nodeitem_objects = NodeItemMenu(None, None)
        self._nodeitems = {}
        self._nodeitem_names = []
        self._nodeitem_trees = {}

    def append(self, node_tree_name, path):
        full_path = ".".join(path)

        if full_path not in self._nodeitem_names:
            self._nodeitem_names.append(full_path)
            self._nodeitem_trees[full_path] = []

            item = NodeItem(self, path[-1], full_path)
            self._nodeitems[path] = item
            child = item

            for key_index in range(len(path) - 1, 0, -1):
                path_slice = path[:key_index]
                if path_slice not in self._nodeitems:
                    path_component = path[key_index - 1]
                    make_panel = (key_index == 1)
                    menu = NodeItemMenu(path_component, path_slice, make_panel)
                    menu.register()

                    self._nodeitems[path_slice] = menu

                else:
                    menu = self._nodeitems[path_slice]

                if child not in menu.children:
                    menu.children.append(child)

                child = menu

            if child not in self._nodeitem_objects.children:
                self._nodeitem_objects.children.append(child)

        self._nodeitem_trees[full_path].append(node_tree_name)

    def remove(self, node_tree_name, key):
        # TODO implement nodeitem remove
        raise NotImplementedError

    def rename(self, old_node_tree_name, new_node_tree_name):
        for full_key, node_trees in self._nodeitem_trees.items():
            if not old_node_tree_name in node_trees:
                continue

            node_trees[node_trees.index(old_node_tree_name)] = new_node_tree_name

    def draw_menu(self, struct, context):
        menu = self._nodeitem_objects
        if not menu._active(context):
            return

        menu.draw(struct.layout, context)

    def register(self):
        bpy.types.NODE_MT_add.append(self.draw_menu)

    def unregister(self):
        bpy.types.NODE_MT_add.remove(self.draw_menu)