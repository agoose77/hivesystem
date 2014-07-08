import bpy
import os

from ..worker import WorkerFinder
from . import Node, NodeSocket

from .BlendNodeTreeManager import HiveMapNodeTreeManager, WorkerMapNodeTreeManager, SpyderMapNodeTreeManager

from .NodeItemManager import NodeItemManager
from .NodeTrees import HiveNodeTree

from bpy.app.handlers import persistent

from .BlenderTextWidget import BlenderTextWidget, manager as text_widget_manager
from .BlenderWidgets import BlenderOptionWidget, BlenderLabelWidget
from . import BlenderPopup


@persistent
def loadblock(dummy):
    blendmanager._loading = True


@persistent
def load(dummy):
    blendmanager.blend_load()


@persistent
def save(dummy):
    blendmanager.blend_save()


@persistent
def update(dummy):
    blendmanager.blend_update()


@persistent
def game_pre(dummy):
    blendmanager.game_pre()


@persistent
def game_post(dummy):
    blendmanager.game_post()


def clear_hive_node_trees():
    for node_tree in bpy.data.node_groups:
        if not isinstance(node_tree, HiveNodeTree):
            continue

        BlendManager._clear_nodetree(node_tree)


def read_conf(block):
    if block in bpy.data.texts:
        return bpy.data.texts[block].as_string().splitlines()

    else:
        filepath = bpy.path.abspath("//" + block)
        if os.path.exists(filepath):
            opened_file = open(filepath)
            contents = opened_file.readlines()
            opened_file.close()

            return contents

        else:
            if block == "hivegui.conf":
                return "spydermodels.*", "workers.*", "spyderhives.*", "spydermaps.*", "hivemaps.*"

            else:
                raise ValueError(block)  # #TODO: add "workergui.conf", "spydergui.conf"


def bpy_opener(block):
    import io

    if not block.startswith("//"):
        return open(block, "r")
    block = block[len("//"):]
    block2 = block.replace(os.sep, "/")
    if block2 in bpy.data.texts:
        text = bpy.data.texts[block2]
        return io.StringIO(text.as_string())
    else:
        return open(block, "r")


def bpy_lister(block):
    import os

    if not block.startswith("//"): return os.listdir(block)
    block = block[len("//"):]
    block2 = block.replace(os.sep, "/")

    ret = []
    for text in bpy.data.texts:
        if text.name.startswith(block2 + "/"): ret.append(text.name[len(block2) + 1:])
    try:
        files = os.listdir(block)
        for f in files:
            if f not in ret: ret.append(f)
    except FileNotFoundError:
        pass
    return ret


class BlendManager:
    """
    Singleton class, maintains hooks and spawns a BlendNodeTreeManager for every nodetree-hivemap pair
    """

    def __init__(self, currdir, hiveguidir):
        self.currdir = currdir
        self.hiveguidir = hiveguidir
        self.nodetrees = []
        self.nodeitemmanager = NodeItemManager()
        self.blend_nodetree_managers = {}
        self._loading = False
        self._restore_editors = {}
        self._old_directory = None
        self._scheduled = []
        self._activated = False

        self.popup_callbacks = {}

        self.last_nodetree = None

    @staticmethod
    def get_escaped_name(name):
        return name.replace(".", "_")

    def get_popup_data(self, popup_id):
        """Return the popup data for a given popup id

        :param popup_id: ID of popup menu
        """
        return self.popup_callbacks[popup_id]

    def save_popup_data(self, popup_id, options, callback):
        """Store popup callback for popup menu

        :param popup_id: ID of popup menu
        :param callback: callback to invoke for menu
        """
        def wrapper(*args, **kwargs):
            """Wrapper to prevent callback entering update loop"""
            self._loading = True
            callback(*args, **kwargs)
            self._loading = False

            self.popup_callbacks.pop(popup_id)

        self.popup_callbacks[popup_id] = options, wrapper

    def popup_select(self, result):
        assert result in self.popup_options, result
        i = self.popup_options.index(result)
        self._loading = True  # otherwise Blender crashes...
        self.popup_callbacks[i]()
        self._loading = False

    def filesaver(self, filename, content):
        if filename not in bpy.data.texts:
            bpy.data.texts.new(filename)
        txt = bpy.data.texts[filename]
        txt.from_string(content)

    def register(self):
        bpy.app.handlers.scene_update_pre.append(update)
        bpy.app.handlers.save_pre.append(save)
        bpy.app.handlers.load_pre.append(loadblock)
        bpy.app.handlers.load_post.append(load)

        # for vanilla Blender, then you can run BGE just once...
        try:
            bpy.app.handlers.game_pre.append(game_pre)
            bpy.app.handlers.game_post.append(game_post)
        except AttributeError:
            pass

        self.nodeitemmanager.register()

        Node.register()
        NodeSocket.register()
        BlenderPopup.register()

    def unregister(self):
        bpy.app.handlers.scene_update_pre.remove(update)
        bpy.app.handlers.save_pre.remove(save)
        bpy.app.handlers.load_pre.remove(loadblock)
        bpy.app.handlers.load_post.remove(load)

        try:
            bpy.app.handlers.game_pre.remove(game_pre)
            bpy.app.handlers.game_post.remove(game_post)

        # for vanilla Blender, then you can run BGE just once...
        except AttributeError:
            pass

        self.nodeitemmanager.unregister()

        Node.unregister()
        NodeSocket.unregister()
        BlenderPopup.unregister()

    def discover_nodes_hivemap(self):
        locationconfs = [self.currdir + os.sep + "locations.conf"]
        locationmodules, syspath = \
            WorkerFinder.find_locationmodules(locationconfs)
        self._workerfinder_global_hivemap = WorkerFinder(locationmodules, [self.hiveguidir] + syspath)

        localdir = bpy.path.abspath("//")
        localconfs = ["hivegui.conf"]
        locationmodules, syspath = \
            WorkerFinder.find_locationmodules(localconfs, localdir, readlines=read_conf)
        found = self._workerfinder_global_hivemap._found_workers

        self._workerfinder_local_hivemap = None
        if use_hive_get(bpy.context.scene):
            self._workerfinder_local_hivemap = WorkerFinder( \
                locationmodules, syspath, found, lister=bpy_lister, opener=bpy_opener
            )

    def discover_nodes_workermap(self):
        seg = [
            "segments.antenna",
            "segments.output",
            "segments.variable",
            "segments.buffer",
            "segments.transistor",
            "segments.modifier",
            "segments.weaver",
            "segments.unweaver",
            "segments.operator",
            "segments.test",
            "segments.custom_code",
        ]
        self._workerfinder_global_workermap = WorkerFinder(seg, [self.hiveguidir])

    def discover_nodes_spydermap(self):
        import copy

        locationconfs = [self.currdir + os.sep + "locations.conf"]
        locationmodules, syspath = \
            WorkerFinder.find_locationmodules(locationconfs)
        self._workerfinder_global_spyderhives = \
            copy.copy(WorkerFinder(locationmodules, [self.hiveguidir] + syspath).spyderhives)

        spyderbees = [
            "spyderbees.*",
        ]
        self._workerfinder_global_spydermap = WorkerFinder(spyderbees, [self.hiveguidir])

    def _get_associated_textblocks(self, nodetreename, nodetreeclass):
        name, tree_bl_idname = nodetreename, nodetreeclass
        path_and_names = []
        if tree_bl_idname == "Hivemap":
            underscore_name = self.get_escaped_name(name)
            name_formatter = "%s.hivemap"
            path_and_names.append((name_formatter, underscore_name))
            path_and_names.append(("hivemaps/" + name_formatter, underscore_name))

        elif tree_bl_idname == "Workermap":
            names0 = [name]
            if name.endswith("-worker"):
                names0.append(name[:-len("-worker")])

            for nam in names0:
                underscore_name = self.get_escaped_name(nam)
                name_formatter = "%s.workermap"
                path_and_names.append((name_formatter, underscore_name))
                path_and_names.append(("workermaps/" + name_formatter, underscore_name))
                name_formatter = "%s.py"
                path_and_names.append(("workers/" + name_formatter, underscore_name))

        elif tree_bl_idname == "Spydermap":
            names0 = [name]
            if name.endswith("-spyder"):
                names0.append(name[:-len("-spyder")])
            for nam in names0:
                underscore_name = self.get_escaped_name(nam)
                name_formatter = "%s.spydermap"
                path_and_names.append((name_formatter, underscore_name))
                path_and_names.append(("spydermaps/" + name_formatter, underscore_name))

        ret = []
        for nam in path_and_names:
            if nam[0] % nam[1] in bpy.data.texts:
                ret.append(nam)
        return ret

    @staticmethod
    def _clear_nodetree(nodetree):
        nodetree.links.clear()
        nodetree.nodes.clear()

    @staticmethod
    def _rename_text(current_name, new_name):
        text_block_data = bpy.data.texts[current_name].as_string()
        if new_name not in bpy.data.texts:
            bpy.data.texts.new(new_name)

        bpy.data.texts[new_name].from_string(text_block_data)

        current_text_block = bpy.data.texts[current_name]
        bpy.data.texts.remove(current_text_block)

    def _remove_nodetree(self, name):
        node_tree = bpy.data.node_groups[name]
        bpy.data.node_groups.remove(node_tree)
        import logging
        logging.info("Removing node tree {}".format(name))

        # Find nodetree
        for index, (nodetree_name, nodetree_bl_idname) in enumerate(self.nodetrees):
            if nodetree_name == name:
                break

        else:
            raise KeyError(name)

        self.nodetrees.pop(index)
        del self.blend_nodetree_managers[name]

        blocks = self._get_associated_textblocks(name, nodetree_bl_idname)

        for block in blocks:
            name = block[0] % block[1]

            text_block = bpy.data.texts[name]
            bpy.data.texts.remove(text_block)

    def check_hivemap_change(self):
        space = bpy.context.space_data
        if space is None:
            return

        if not hasattr(space, "tree_type"):
            return

        if space.tree_type not in ("Hivemap", "Workermap", "Spydermap"):
            return

        if space.edit_tree is None:
            return

        nodetree = space.edit_tree.name
        if nodetree == self.last_nodetree:
            return

        self.last_nodetree = nodetree
        if not nodetree in self.blend_nodetree_managers:
            return

        manager = self.blend_nodetree_managers[nodetree]
        if space.tree_type == "Spydermap":
            spyderhive = manager.spydermapmanager._spyderhive
            manager.psh.update_spyderhive(spyderhive)

    def on_added_node_trees(self, added_node_tree_names):
        """Handle added node groups

        :param added_node_tree_names: list of added hive node tree names
        """

        import Spyder
        from .NodeTrees import HivemapNodeTree, WorkermapNodeTree, SpydermapNodeTree

        node_trees = bpy.data.node_groups
        for node_tree_name in added_node_tree_names:
            node_tree = node_trees[node_tree_name]
            tree_name = tree_text_name = str(node_tree_name)

            escaped_name = self.get_escaped_name(tree_text_name)
            node_tree.registered_name = tree_name

            try:
                if isinstance(node_tree, HivemapNodeTree):
                    manager_class = HiveMapNodeTreeManager
                    file_name = escaped_name + ".hivemap"
                    tree_text_name = "hivemaps/" + file_name

                    if tree_text_name not in bpy.data.texts and file_name not in bpy.data.texts:
                        map_object = Spyder.Hivemap([], [])
                        map_string = str(map_object)
                        bpy.data.texts.new(tree_text_name)
                        bpy.data.texts[tree_text_name].from_string(map_string)

                    elif tree_text_name in bpy.data.texts:
                        map_object = Spyder.Hivemap(bpy.data.texts[tree_text_name].as_string())

                    else:
                        map_object = Spyder.Hivemap(bpy.data.texts[file_name].as_string())

                elif isinstance(node_tree, WorkermapNodeTree):
                    manager_class = WorkerMapNodeTreeManager
                    tree_text_name = "workermaps/" + escaped_name + ".workermap"
                    if not tree_text_name in bpy.data.texts:
                        map_object = Spyder.Workermap([], [])
                        map_string = str(map_object)
                        bpy.data.texts.new(tree_text_name)
                        bpy.data.texts[tree_text_name].from_string(map_string)

                    else:
                        map_object = Spyder.Workermap(bpy.data.texts[tree_text_name].as_string())

                elif isinstance(node_tree, SpydermapNodeTree):
                    manager_class = SpyderMapNodeTreeManager
                    tree_text_name = "spydermaps/" + escaped_name + ".spydermap"
                    if not tree_text_name in bpy.data.texts:
                        map_object = Spyder.Spydermap("bee.spyderhive.spyderframe", [], [])
                        map_string = str(map_object)
                        bpy.data.texts.new(tree_text_name)
                        bpy.data.texts[tree_text_name].from_string(map_string)

                    else:
                        map_object = Spyder.Spydermap(bpy.data.texts[tree_text_name].as_string())

                else:
                    raise TypeError(node_tree)

                node_tree_manager = manager_class(self, tree_name)
                self.blend_nodetree_managers[tree_name] = node_tree_manager

                import logging
                logging.info("Adding node tree {}".format(tree_name))

                if isinstance(node_tree, HivemapNodeTree):
                    node_tree_manager.hivemapmanager._load(map_object)

                elif isinstance(node_tree, WorkermapNodeTree):
                    node_tree_manager.workermapmanager._load(map_object)

                elif isinstance(node_tree, SpydermapNodeTree):
                    node_tree_manager.spydermapmanager._load(map_object)

            finally:
                for name, _ in self.nodetrees:
                    if name == tree_name:
                        return

                self.nodetrees.append((tree_name, manager_class.tree_bl_idname))

    def on_renamed_node_trees(self, renamed_node_tree_names):
        """Handle renamed node groups

        :param renamed_node_tree_names: list of renamed hive node tree names
        """
        # Rename NodeTree
        node_trees = bpy.data.node_groups
        for new_name in renamed_node_tree_names:
            node_tree = node_trees[new_name]
            old_name = node_tree.registered_name
            node_tree.registered_name = new_name

            tree_bl_idname = node_tree.bl_idname

            node_tree_manager = self.blend_nodetree_managers.pop(old_name)
            node_tree_manager.name = new_name

            self.nodeitemmanager.rename(old_name, new_name)
            self.blend_nodetree_managers[new_name] = node_tree_manager

            new_name_underscores = self.get_escaped_name(new_name)
            stripped_new_name_underscores = new_name_underscores

            old_name_underscores = self.get_escaped_name(old_name)
            stripped_old_name_underscores = old_name_underscores

            blocks = self._get_associated_textblocks(old_name, tree_bl_idname)

          #  for node_tree in node_tree_names:
            if tree_bl_idname == "Hivemap":
                pass

            elif tree_bl_idname == "Workermap":
                if old_name.endswith("-worker"):
                    stripped_old_name_underscores = old_name[:-len("-worker")]

                if new_name.endswith("-worker"):
                    stripped_new_name_underscores = new_name[:-len("-worker")]

            elif tree_bl_idname == "Spydermap":
                if old_name.endswith("-spyder"):
                    stripped_old_name_underscores = old_name[:-len("-spyder")]

                if new_name.endswith("-spyder"):
                    stripped_new_name_underscores = new_name[:-len("-spyder")]

            for block in blocks:
                path, new_name = block
                if new_name == old_name_underscores:
                    new_file_name = new_name_underscores

                elif new_name == stripped_old_name_underscores:
                    new_file_name = stripped_new_name_underscores

                else:
                    raise ValueError(new_name)

                text1 = path % new_name
                text2 = path % new_file_name

                import logging
                logging.info("Renaming node tree {}".format(new_name))

                self._rename_text(text1, text2)

        hive_node_groups = {node_tree.name: node_tree for node_tree in bpy.data.node_groups
                            if isinstance(node_tree, HiveNodeTree) if node_tree.users}
        self.nodetrees = [(node_tree_name, node_tree.bl_idname) for node_tree_name, node_tree
                          in hive_node_groups.items()]

    def on_deleted_node_trees(self, removed_node_tree_names):
        """Handle deleted node groups

        :param removed_node_tree_names: list of removed hive node tree names
        """
        remove_node_tree = self._remove_nodetree

        for name in removed_node_tree_names:
            remove_node_tree(name)

    def blend_update(self, *args):
        """Handle blend file updates"""
        from .NodeTrees import HiveNodeTree, HivemapNodeTree, WorkermapNodeTree, SpydermapNodeTree

        if self._loading:
            return

        self._do_schedule()
        self.check_hivemap_change()

        node_tree_names = [name for name, _ in self.nodetrees]
        hive_node_groups = [node_tree.name for node_tree in bpy.data.node_groups
                            if isinstance(node_tree, HiveNodeTree) if node_tree.users]

        if set(hive_node_groups) != set(node_tree_names):

            if len(node_tree_names) < len(hive_node_groups):
                # Handle added node trees
                added_nodes = list(set(hive_node_groups).difference(node_tree_names))
                self.on_added_node_trees(added_nodes)

            elif len(node_tree_names) > len(hive_node_groups):
                # Handle deleted node trees
                removed_nodes = list(set(node_tree_names).difference(hive_node_groups))
                self.on_deleted_node_trees(removed_nodes)

            else:
                # Handle renamed nodes
                renamed_nodes = [name for name in hive_node_groups
                                 if bpy.data.node_groups[name].registered_name != name]
                self.on_renamed_node_trees(renamed_nodes)

        text_widget_manager.check_update()

    def get_textblock_name(self, nodetree_manager):
        name = nodetree_manager.name
        escaped_name = self.get_escaped_name(name)

        if isinstance(nodetree_manager, HiveMapNodeTreeManager):
            file_name = "%s.hivemap" % escaped_name
            file_folder = "hivemaps/" + file_name
            full_name = file_name if file_name in bpy.data.texts else file_folder

        elif isinstance(nodetree_manager, WorkerMapNodeTreeManager):
            if name.endswith("-worker"):
                name = name[:-len("-worker")]

            file_name = "{}.workermap".format(escaped_name)
            file_folder = "workermaps/{}".format(file_name)
            full_name = file_name if file_name in bpy.data.texts else file_folder

        elif isinstance(nodetree_manager, SpyderMapNodeTreeManager):
            if name.endswith("-spyder"):
                name = name[:-len("-spyder")]

            file_name = "{}.spydermap".format(escaped_name)
            file_folder = "spydermaps/{}".format(file_name)
            full_name = file_name if file_name in bpy.data.texts else file_folder

        else:
            raise TypeError("NodeTree manager type unrecognised")

        return full_name

    def _sync_nodetree_to_text(self):
        """
        Synchronizes the nodetrees onto text blocks
        #TODO: skip this if the nodetree is in an uneditable state
        """
        import sys, imp
        from ..workergen import workergen

        for nodetree_manager in self.blend_nodetree_managers.values():
            name = nodetree_manager.name
            escaped_name = self.get_escaped_name(name)

            file_name = self.get_textblock_name(nodetree_manager)

            if isinstance(nodetree_manager, HiveMapNodeTreeManager):
                nodetree_manager.hivemapmanager.save(file_name, self.filesaver)

            elif isinstance(nodetree_manager, WorkerMapNodeTreeManager):
                workermap = nodetree_manager.workermapmanager.save(file_name, self.filesaver)
                classname = escaped_name.split("/")[-1]
                code = workergen(classname, workermap)
                blockname = "workers/{}.py".format(escaped_name)
                self.filesaver(blockname, code)

            elif isinstance(nodetree_manager, SpyderMapNodeTreeManager):
                nodetree_manager.spydermapmanager.save(file_name, self.filesaver)

        if self._workerfinder_local_hivemap:
            local_modules = self._workerfinder_local_hivemap._done_mods
            # cyclic dependencies suck, but should be rare... hopefully this will do it...
            # TODO, look into a more robust alternative
            for _ in range(10):
                for modname in list(sys.modules):
                    module = sys.modules[modname]
                    if id(module) in local_modules:
                        try:
                            imp.reload(module)

                        except:
                            import traceback
                            traceback.print_exc()

    def _sync_text_to_nodetree(self):
        """
        Synchronizes the text blocks onto the nodetrees
        #Does not detect if custom workers and Spyder models have changed
        #TODO: error detection => uneditable state?
        """
        clear_hive_node_trees()

        self._load_hivemaps()
        self._load_workermaps()
        self._load_spydermaps()

    def for_valid_texts(self, extension, folder_name, tree_suffix, tree_manager_class, callback):
        """Load HIVE files from text blocks

        :param extension: valid extension for file
        :param folder_name: valid folder name to strip
        :param tree_suffix: suffix to append if folder name is present
        :param tree_manager_class: class for NodeTree manager
        :param callback: callback to load data
        """
        for text_block in bpy.data.texts:

            try:
                text_block_name = text_block.name

                extension_string = ".{}".format(extension)
                extension_length = len(extension_string)
                if text_block_name.endswith(extension_string):
                    nodetree_name = text_block_name[:-extension_length]

                    folder_string = "{}/".format(folder_name)
                    folder_length = len(folder_string)

                    if nodetree_name.startswith(folder_string):
                        nodetree_name = nodetree_name[folder_length:] + tree_suffix

                    # Find existing nodetree
                    for nodetree in bpy.data.node_groups:
                        node_group_name = nodetree.name

                        if node_group_name == nodetree_name:
                            break

                        node_group_name = node_group_name.replace(".", "_")
                        if node_group_name == nodetree_name:
                            break

                    else:
                        nodetree = None

                    import logging
                    if nodetree is None:
                        logging.info("Creating new node tree (group)")
                        nodetree = bpy.data.node_groups.new(nodetree_name, tree_manager_class.tree_bl_idname)
                        # Allow checks for renaming
                        nodetree.registered_name = nodetree_name

                    # Ensure we load users
                    for space in (sp for s in bpy.data.screens for a in s.areas for sp in a.spaces if sp.type == "NODE_EDITOR"):
                        if space.tree_type != tree_manager_class.tree_bl_idname:
                            continue

                        space.node_tree = nodetree
                        logging.info("Loading space to preserve users")
                        break

                    nodetree_name = nodetree.name
                    if nodetree_name not in self.blend_nodetree_managers:
                        nodetree_manager = tree_manager_class(self, nodetree_name)
                        self.nodetrees.append((nodetree_name, tree_manager_class.tree_bl_idname))
                        self.blend_nodetree_managers[nodetree_name] = nodetree_manager
                        logging.info("Creating new node tree manager")

                    nodetree_manager = self.blend_nodetree_managers[nodetree_name]
                    text_block = bpy.data.texts[text_block_name]

                    callback(nodetree_manager, text_block)

            except:
                import logging
                import traceback
                traceback.print_exc()
                logging.critical("Nodetree import failed {}".format(text_block.name))

    def _load_hivemaps(self):
        """Load hivemaps from text blocks"""

        def load_callback(nodetree_manager, text_block):
            import spyder
            import Spyder

            hivemap_string = text_block.as_string()
            data = spyder.core.parse(hivemap_string)[1]

            hivemap = Spyder.Hivemap.fromdict(data)
            nodetree_manager.hivemapmanager._load(hivemap)

        self.for_valid_texts("hivemap", "hivemaps", "", HiveMapNodeTreeManager, load_callback)

    def _load_workermaps(self):
        """Load workermaps from text blocks"""

        def load_callback(nodetree_manager, text_block):
            import spyder
            import Spyder
            workermap_string = text_block.as_string()
            data = spyder.core.parse(workermap_string)[1]

            workermap = Spyder.Workermap.fromdict(data)
            nodetree_manager.workermapmanager._load(workermap)

        self.for_valid_texts("workermap", "workermaps", "-worker", WorkerMapNodeTreeManager, load_callback)

    def _load_spydermaps(self):
        """Load spydermaps from text blocks"""

        def load_callback(nodetree_manager, text_block):
            import Spyder

            spydermap = Spyder.Spydermap.fromfile("//{}".format(text_block.name))
            nodetree_manager.spydermapmanager._load(spydermap)

        self.for_valid_texts("spydermap", "spydermaps", "-spyder", SpyderMapNodeTreeManager, load_callback)

    def activate(self):
        """Discovers all nodes"""
        #TODO: support re-discovery ("node sync"), also of Spyder models
        self.discover_nodes_hivemap()
        self.discover_nodes_workermap()
        self.discover_nodes_spydermap()
        self._activated = True

    def save_last_hive_level(self):
        """Save the current value of the hive level"""
        global _last_hive_level
        if bpy.context is not None:
            hive_level = getattr(bpy.context, "hive_level", None)
            if hive_level is not None:
                hive_level = int(hive_level)
            _last_hive_level = hive_level

    def blend_load(self):
        import logging
        logging.info("Hive loading hook: {}".format(bpy.data.texts))

        self.spyderhive_widget = BlenderOptionWidget(None, "", [])
        # self.docstring_widget = BlenderTextWidget(None, "Docstring")

        self.blend_nodetree_managers.clear()
        self.nodetrees = []
        self.activate()

        try:
            self._sync_text_to_nodetree()

        finally:
            self._loading = False
            self.blend_update()

        logging.info("Hive loading hook complete")

    def _blend_save(self):
        self._sync_nodetree_to_text()

    def blend_save(self, *args):
        import logging
        logging.info("Hive saving hook")
        # TODO what happens if this causes an exception, does this prevent the save? better take no chances..
        try:
            self._blend_save()

        except:
            logging.exception("Saving failed")

    def get_nodetree_manager(self, name):
        return self.blend_nodetree_managers[name]

    def game_pre(self):
        """Callback for pre-game playback"""
        self._sync_nodetree_to_text()
        import os
        import sys

        self._old_directory = os.getcwd()
        os.chdir(bpy.path.abspath("//"))

        import imp
        import bee.blendsupport
        import bee.blendsupport.blendblockimporter

        for hook in list(sys.path_hooks):
            if hasattr(hook, "__name__") and hook.__name__ == "blendblockimporter":
                sys.path_hooks.remove(hook)

        imp.reload(bee.blendsupport)
        imp.reload(bee.blendsupport.blendblockimporter)

        # clear Spyder file cache
        import inspect, spyder, Spyder

        inspect.getmodule(Spyder.Resource)._resources.clear()

    def game_post(self):
        """Callback for post-game playback"""
        import os
        import libcontext

        # Python runtime remains loaded, so clear game-data
        libcontext._contexts.clear()
        if self._old_directory is not None:
            os.chdir(self._old_directory)
            self._old_directory = None

    def schedule(self, callback):
        self._scheduled.append(callback)

    def _do_schedule(self):
        while self._scheduled:
            callback = self._scheduled.pop(0)
            callback()

    def morph_state(self, current_profile, new_profile):
        """Morph workers to a different profile state"""
        for blend_nodetree_manager in self.blend_nodetree_managers.values():
            if not isinstance(blend_nodetree_manager, HiveMapNodeTreeManager):
                continue

            worker_instance_manager = blend_nodetree_manager.workerinstancemanager
            worker_instance_manager.default_profile = new_profile

            for worker_id in worker_instance_manager.get_workerinstances():
                worker_instance = worker_instance_manager.get_workerinstance(worker_id)
                if worker_instance.curr_profile != current_profile:
                    continue

                try:
                    worker_instance_manager.morph_worker(worker_id, new_profile)

                except KeyError:
                    pass

    def simplify_all(self):
        """Morph workers to simplified state"""
        self.morph_state("default", "simplified")

    def unsimplify_all(self):
        """Morph workers to default state"""
        self.morph_state("simplified", "default")


blendmanager = None


def initialize(*args, **kargs):
    global blendmanager
    if blendmanager is not None:
        return

    blendmanager = BlendManager(*args, **kargs)


def unregister():
    global blendmanager
    if blendmanager is None:
        return

    blendmanager.unregister()
    blendmanager = None


def get_defaultproject_data():
    data = []
    bpdir = blendmanager.currdir + os.sep + "blenderproject"

    assert os.path.exists(bpdir), bpdir
    cwd = os.path.abspath(os.getcwd())

    try:
        os.chdir(os.path.abspath(bpdir))

        files = []
        for root, directories, directory_files in os.walk('.'):
            removed = "__pycache__", ".svn", ".bzr"
            for removable in removed:
                if removable in directories:
                    directories.remove(removable)

            for name in directory_files:
                if name.endswith("~") or name.endswith(".pyc"):
                    continue

                files.append(os.path.join(root, name))

        for filename in files:
            block = filename.replace(os.sep, "/")

            if block.startswith("./"):
                block = block[2:]

            opened_file = open(filename)
            content = opened_file.read()
            opened_file.close()

            data.append((block, content))

    finally:
        os.chdir(cwd)

    return data


def enable_hive(scene, import_data):
    if not blendmanager._activated:
        blendmanager.activate()

    data = import_data
    for block, content in data:
        if block in bpy.data.texts:
            old_content = bpy.data.texts[block].as_string()
            if old_content != content:
                import logging
                logging.debug("Enabling Hive system: Blender text block '%s' already exists" % block)

    main = [block for block, content in data if block.find("/") == -1 and block.endswith(".py")]

    if len(main) == 0:
        raise Exception("Could not find main script in default Blender project")

    if len(main) > 1:
        raise Exception("Multiple main script candidates in default Blender project: {}".format(main))

    for block, content in data:
        if block not in bpy.data.texts:
            bpy.data.texts.new(block)
            bpy.data.texts[block].from_string(content)

    scene["__main__"] = main[0]

    try:
        blendmanager._loading = True
        blendmanager._sync_text_to_nodetree()

    finally:
        blendmanager._loading = False


def disable_hive(scene):
    data = get_defaultproject_data()
    for block, content in data:
        if block in bpy.data.texts:
            old_content = bpy.data.texts[block].as_string()

            if old_content == content:
                bpy.data.texts.remove(bpy.data.texts[block])

    del scene["__main__"]


def use_hive_get(scene):
    if scene is None:
        return False

    if "__main__" in scene and scene["__main__"]:
        return 1

    else:
        return 0


def use_hive_set(scene, value):
    global _last_hive_level

    if blendmanager is None:
        return

    if scene is None:
        return

    current = use_hive_get(scene)
    if value == current:
        return

    if value:
        data = get_defaultproject_data()
        enable_hive(scene, data)
        _last_hive_level = 1

    else:
        disable_hive(scene)


_last_hive_level = None


def change_hive_level(screen, context):
    global _last_hive_level

    try:
        current_level = int(screen.hive_level)

    except TypeError:
        return

    if _last_hive_level == current_level:
        return

    if _last_hive_level is not None:
        if current_level == 1:
            blendmanager.simplify_all()

        elif _last_hive_level == 1:
            blendmanager.unsimplify_all()

    _last_hive_level = current_level


