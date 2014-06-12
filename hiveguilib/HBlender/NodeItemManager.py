import bpy
from . import scalepos, unscalepos, level


class AddHiveNode(bpy.types.Operator):
    bl_idname = "node.add_hive_node"
    bl_label = "Add a Hive system node to the Node Editor"

    type = bpy.props.StringProperty()

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            x, y = context.space_data.cursor_location
            node = context.active_node
            if node is None:
                return {'FINISHED'}
            node.location = x, y

        elif event.type == 'LEFTMOUSE':
            return {'FINISHED'}

        elif event.type in ('RIGHTMOUSE', 'ESC'):
            nodetree = context.space_data.edit_tree
            node = context.active_node
            nodetree.nodes.remove(node)
            return {'CANCELLED'}
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        # In Qt, dragged widgets generate their own events
        #In Blender, we have to contact the clipboard directly
        from . import BlendManager

        nodetreename = context.space_data.edit_tree.name
        print("ADD NODE", self.type, nodetreename)
        add_node = bpy.types.NODE_OT_add_node
        add_node.store_mouse_cursor(context, event)
        x, y = unscalepos(context.space_data.cursor_location)

        bntm = BlendManager.blendmanager.blend_nodetree_managers[nodetreename]
        pwc = bntm.pwc
        pwc._select_worker(tuple(self.type.split(".")))
        clip = bntm.clipboard
        clip.drop_worker(x, y)

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


bpy.utils.register_class(AddHiveNode)


class NodeItem:
    def __init__(self, manager, key, fullkey):
        self.manager = manager
        self.key = key
        self.fullkey = fullkey

    def _active(self, context):
        if context.space_data.edit_tree is None: return False
        if context.space_data.edit_tree.name not in self.manager._nodeitem_trees[self.fullkey]: return False
        if not level.active(context, tuple(self.fullkey.split("."))): return
        return True

    def draw(self, layout, context):
        default_context = bpy.app.translations.contexts.default
        props = layout.operator("node.add_hive_node", text=self.key, text_ctxt=default_context)
        props.type = self.fullkey


class NodeItemMenu:
    name = "NODE_MT_HIVE"

    def __init__(self, title, fullname, make_panel=False):
        if title is not None: assert fullname is not None
        self.title = title
        self.fullname = fullname
        self.children = []

        def menudraw(struct, context):
            if not level.active(context, self.fullname): return
            return self.draw(struct.layout, context)

        d = dict(
            bl_space_type='NODE_EDITOR',
            bl_label="<HiveMenu>",
            draw=menudraw,
            poll=self.poll,
        )
        n = self.name
        if self.fullname is not None: n = self.name + "_" + "_".join(self.fullname)
        self.name = n
        self.menuclass = type(n, (bpy.types.Menu,), d)
        bpy.utils.register_class(self.menuclass)
        if make_panel:
            nn = n.replace("NODE_MT_", "NODE_PT_")
            d = dict(
                bl_space_type='NODE_EDITOR',
                bl_label=title,
                bl_region_type='TOOLS',
                bl_options={'DEFAULT_CLOSED'},
                poll=self._active,
                draw=menudraw,
            )
            self.panelclass = type(nn, (bpy.types.Panel,), d)
            bpy.utils.register_class(self.panelclass)

    def _active(self, context):
        if not level.active(context, self.fullname): return False
        for child in self.children:
            if child._active(context): return True
        return False

    def draw(self, layout, context):
        col = layout.column()
        for child in self.children:
            if not child._active(context): continue
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

    def append(self, nodetreename, key):
        # print("NodeItemManager ADD", nodetreename, key)
        fullkey = ".".join(key)
        if fullkey not in self._nodeitem_names:
            self._nodeitem_names.append(fullkey)
            self._nodeitem_trees[fullkey] = []

            item = NodeItem(self, key[-1], fullkey)
            self._nodeitems[key] = item
            child = item
            for n in range(len(key) - 1, 0, -1):
                partkey = key[:n]
                if partkey not in self._nodeitems:
                    k = key[n - 1]
                    make_panel = (n == 1)
                    menu = NodeItemMenu(k, partkey, make_panel)
                    self._nodeitems[partkey] = menu
                else:
                    menu = self._nodeitems[partkey]
                if child not in menu.children:
                    menu.children.append(child)
                child = menu
            if child not in self._nodeitem_objects.children:
                self._nodeitem_objects.children.append(child)
        self._nodeitem_trees[fullkey].append(nodetreename)

    def remove(self, nodetreename, key):
        print("NodeItemManager REMOVE", nodetreename, key)
        raise NotImplementedError

    def draw_menu(self, struct, context):
        menu = self._nodeitem_objects
        if not menu._active(context): return
        menu.draw(struct.layout, context)

    def register(self):
        bpy.types.NODE_MT_add.append(self.draw_menu)

    def unregister(self):
        bpy.types.NODE_MT_add.remove(self.draw_menu)