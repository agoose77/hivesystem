import bpy
import os

from ..worker import WorkerFinder
from . import Node, NodeSocket

from .BlendNodeTreeManager import BlendNodeTreeManager

from .NodeItemManager import NodeItemManager
from .NodeTree import HiveNodeTree

from bpy.app.handlers import persistent

from . import BlenderTextWidget, BlenderPopup
from .BlenderWidgets import BlenderOptionWidget


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


def get_nodetree_spaces():
    nodetree_editors = {}

    for screen in bpy.data.screens:
        for area in screen.areas:
            for space in area.spaces:
                if space.type != 'NODE_EDITOR':
                    continue

                node_tree = space.edit_tree
                if not isinstance(node_tree, HiveNodeTree):
                    continue

                name = node_tree.name
                BlendManager._clear_nodetree(node_tree)

                if name not in nodetree_editors:
                    nodetree_editors[name] = []

                nodetree_editors[name].append(space)
    return nodetree_editors


def read_conf(block):
    if block in bpy.data.texts:
        return bpy.data.texts[block].as_string().splitlines()

    else:
        filepath = bpy.path.abspath("//" + block)
        if os.path.exists(filepath):
            opened_file = open(filepath)
            contents = opened_file.splitlines()
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
        self._olddir = None
        self._scheduled = []
        self._activated = False

        self.popup_window = None
        self.popup_options = None
        self.popup_callbacks = None

        self.last_nodetree = None

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
        try:
            bpy.app.handlers.game_pre.append(game_pre)
            bpy.app.handlers.game_post.append(game_post)
        except AttributeError:  # for vanilla Blender, then you can run BGE just once...
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
        except AttributeError:  # for vanilla Blender, then you can run BGE just once...
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
        if use_hive_get(bpy.context):
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
        name, c = nodetreename, nodetreeclass
        nams = []
        if c == "Hivemap":
            p = name.replace(".", "_")
            n0 = "%s.hivemap"
            nams.append((n0, p))
            nams.append(("hivemaps/" + n0, p))
        elif c == "Workermap":
            names0 = [name]
            if name.endswith("-worker"): names0.append(name[:-len("-worker")])
            for nam in names0:
                p = nam.replace(".", "_")
                n0 = "%s.workermap"
                nams.append((n0, p))
                nams.append(("workermaps/" + n0, p))
                n0 = "%s.py"
                nams.append(("workers/" + n0, p))
        elif c == "Spydermap":
            names0 = [name]
            if name.endswith("-spyder"): names0.append(name[:-len("-spyder")])
            for nam in names0:
                p = nam.replace(".", "_")
                n0 = "%s.spydermap"
                nams.append((n0, p))
                nams.append(("spydermaps/" + n0, p))

        ret = []
        for nam in nams:
            if nam[0] % nam[1] in bpy.data.texts:
                ret.append(nam)
        return ret

    @staticmethod
    def _clear_nodetree(nodetree):
        nodetree.links.clear()
        nodetree.nodes.clear()

    @staticmethod
    def _rename_text(text1, text2):
        txt = bpy.data.texts[text1].as_string()
        if text2 not in bpy.data.texts:
            bpy.data.texts.new(text2)
        bpy.data.texts[text2].from_string(txt)
        try:
            bpy.data.texts[text1].remove()
        except:
            bpy.data.texts[text1].from_string("<DELETED>")


    def _remove_nodetree(self, name):
        # TODO: is not currently triggered from anywhere...
        try:
            bpy.data.node_groups[name].remove()

        except:
            self._clear_nodetree(bpy.data.node_groups[name])

        for i, v in enumerate(self.nodetrees):
            if v[0] == name:
                c = v[1]
                break
        else:
            raise KeyError(name)
        self.nodetrees.pop(i)

        del self.blend_nodetree_managers[name]

        blocks = self._get_associated_textblocks(name, c)
        for block in blocks:
            name = block[0] % block[1]
            try:
                bpy.data.texts[name].remove()
            except:
                bpy.data.texts[name].from_string("<DELETED>")

    def check_hivemap_change(self):
        space = bpy.context.space_data
        if space is None: return
        if not hasattr(space, "tree_type"): return
        if space.tree_type not in ("Hivemap", "Workermap", "Spydermap"): return
        if space.edit_tree is None: return
        nodetree = space.edit_tree.name
        if nodetree != self.last_nodetree:
            self.last_nodetree = nodetree
            if nodetree in self.blend_nodetree_managers:
                manager = self.blend_nodetree_managers[nodetree]
                if space.tree_type == "Spydermap":
                    spyderhive = manager.spydermapmanager._spyderhive
                    manager.psh.update_spyderhive(spyderhive)

    def blend_update(self, *args):
        import spyder, Spyder
        from .NodeTree import HiveNodeTree, HivemapNodeTree, WorkermapNodeTree, SpydermapNodeTree

        if self._loading:
            return
        self._do_schedule()
        self.check_hivemap_change()

        hivenodegroups = [nodetree for nodetree in bpy.data.node_groups \
                          if isinstance(nodetree, HiveNodeTree)]
        hivenodegroupnames = [nodetree.name for nodetree in hivenodegroups]
        nodetrees = [v[0] for v in self.nodetrees]
        if set(hivenodegroupnames) != set(nodetrees):
            if len(nodetrees) < len(hivenodegroupnames):
                for nodetree in hivenodegroups:
                    try:
                        nam = str(nodetree.name)
                        nam0 = nam
                        if nam not in nodetrees:
                            if isinstance(nodetree, HivemapNodeTree):
                                c = "Hivemap"
                                nam2 = nam.replace(".", "_") + ".hivemap"
                                nam = "hivemaps/" + nam2
                                if nam not in bpy.data.texts and nam2 not in bpy.data.texts:
                                    map = Spyder.Hivemap([], [])
                                    txt = str(map)
                                    bpy.data.texts.new(nam)
                                    bpy.data.texts[nam].from_string(txt)
                                else:
                                    map = Spyder.Hivemap(bpy.data.texts[nam].as_string())
                            elif isinstance(nodetree, WorkermapNodeTree):
                                c = "Workermap"
                                nam = "workermaps/" + nam.replace(".", "_") + ".workermap"
                                if not nam in bpy.data.texts:
                                    map = Spyder.Workermap([], [])
                                    txt = str(map)
                                    bpy.data.texts.new(nam)
                                    bpy.data.texts[nam].from_string(txt)
                                else:
                                    map = Spyder.Workermap(bpy.data.texts[nam].as_string())
                            elif isinstance(nodetree, SpydermapNodeTree):
                                c = "Spydermap"
                                nam = "spydermaps/" + nam.replace(".", "_") + ".spydermap"
                                if not nam in bpy.data.texts:
                                    map = Spyder.Spydermap("bee.spyderhive.spyderframe", [], [])
                                    txt = str(map)
                                    bpy.data.texts.new(nam)
                                    bpy.data.texts[nam].from_string(txt)
                                else:
                                    map = Spyder.Spydermap(bpy.data.texts[nam].as_string())
                            else:
                                raise TypeError(nodetree)
                            m = BlendNodeTreeManager(self, nam0, c)
                            self.blend_nodetree_managers[nam0] = m
                            m.start()
                            if isinstance(nodetree, HivemapNodeTree):
                                m.hivemapmanager._load(map)
                                m.workermanager.sync_antennafoldstate()
                            elif isinstance(nodetree, WorkermapNodeTree):
                                m.workermapmanager._load(map)
                            elif isinstance(nodetree, SpydermapNodeTree):
                                m.spydermapmanager._load(map)
                    finally:
                        if nam0 not in nodetrees: self.nodetrees.append((nam0, c))
            elif len(nodetrees) > len(hivenodegroupnames):
                # Not normally triggered, somehow....
                for name, c in list(self.nodetrees):
                    if name in hivenodegroupnames: continue
                    self._remove_nodetree(name)
            else:
                # Rename NodeTree
                #TODO?: Check if instances of this map exist... warn? forbid? delete? rename?
                oldname, newname = None, None
                done = set()
                for name, c0 in list(self.nodetrees):
                    if name in hivenodegroupnames:
                        done.add(name)
                    else:
                        # TODO check node tree contentse to find renamed trees
                        assert oldname is None  #we can't know how to rename more than one NodeTree!
                        oldname = name
                        c = c0
                for name in hivenodegroupnames:
                    if name not in done:
                        assert newname is None
                        newname = name
                        break

                m = self.blend_nodetree_managers.pop(oldname)
                m.name = newname
                self.blend_nodetree_managers[newname] = m
                oldname2, newname2 = oldname, newname
                blocks = self._get_associated_textblocks(oldname, c)

                self.nodetrees = []
                for nodetree in hivenodegroups:
                    if c == "Hivemap":
                        pass
                    elif c == "Workermap":
                        if oldname.endswith("-worker"): oldname2 = oldname[:-len("-worker")]
                        if newname.endswith("-worker"): newname2 = newname[:-len("-worker")]
                    elif c == "Spydermap":
                        if oldname.endswith("-spyder"): oldname2 = oldname[:-len("-spyder")]
                        if newname.endswith("-spyder"): newname2 = newname[:-len("-spyder")]
                for b in blocks:
                    p, n = b
                    if n == oldname:
                        nn = newname
                    elif n == oldname2:
                        nn = newname2
                    else:
                        raise ValueError(n)
                    text1 = p % n
                    text2 = p % nn
                    self._rename_text(text1, text2)

                self.nodetrees = []
                for nodetree in hivenodegroups:
                    if isinstance(nodetree, HivemapNodeTree):
                        c = "Hivemap"
                    elif isinstance(nodetree, WorkermapNodeTree):
                        c = "Workermap"
                    elif isinstance(nodetree, SpydermapNodeTree):
                        c = "Spydermap"
                    self.nodetrees.append((nodetree.name, c))

        if self._restore_editors is not None:
            for tname in self._restore_editors:
                if tname not in nodetrees: continue
                nodetree = bpy.data.node_groups[tname]
                for editor in self._restore_editors[tname]:
                    editor.path.push(nodetree)
        self._restore_editors = None

        BlenderTextWidget.manager.check_update()

    def _sync_nodetree_to_text(self):
        """
        Synchronizes the nodetrees onto text blocks
        #TODO: skip this if the nodetree is in an uneditable state
        """
        import sys, imp
        from ..workergen import workergen

        for ntm in self.blend_nodetree_managers.values():
            if ntm.typ == "Hivemap":
                nam1 = "%s.hivemap" % ntm.name.replace(".", "_")
                nam2 = "hivemaps/" + nam1
                nam = nam1 if nam1 in bpy.data.texts else nam2
                ntm.hivemapmanager.save(nam, self.filesaver)
            elif ntm.typ == "Workermap":
                name = ntm.name
                if name.endswith("-worker"): name = name[:-len("-worker")]
                name = name.replace(".", "_")
                nam1 = "%s.workermap" % name
                nam2 = "workermaps/" + nam1
                nam = nam1 if nam1 in bpy.data.texts else nam2
                workermap = ntm.workermapmanager.save(nam, self.filesaver)
                classname = name.split("/")[-1]
                code = workergen(classname, workermap)
                blockname = "workers/%s.py" % name
                self.filesaver(blockname, code)
            elif ntm.typ == "Spydermap":
                name = ntm.name
                if name.endswith("-spyder"): name = name[:-len("-spyder")]
                name = name.replace(".", "_")
                nam1 = "%s.spydermap" % name
                nam2 = "spydermaps/" + nam1
                nam = nam1 if nam1 in bpy.data.texts else nam2
                ntm.spydermapmanager.save(nam, self.filesaver)

        if self._workerfinder_local_hivemap:
            local_mods = self._workerfinder_local_hivemap._done_mods
            # cyclic dependencies suck, but should be rare... hopefully this will do it...
            # TODO, look into a more robust alternative
            for n in range(10):
                for modname in list(sys.modules):
                    mod = sys.modules[modname]
                    if id(mod) in local_mods:
                        try:
                            imp.reload(mod)
                        except:
                            import traceback

                            traceback.print_exc()


    def _sync_text_to_nodetree(self):
        """
        Synchronizes the text blocks onto the nodetrees
        #Does not detect if custom workers and Spyder models have changed
        #TODO: error detection => uneditable state?
        """
        self._restore_editors = get_nodetree_spaces()
        self._load_hivemaps()
        self._load_workermaps()
        self._load_spydermaps()

    def _load_hivemaps(self):
        for txt in bpy.data.texts:
            if txt.as_string() == "<DELETED>": continue
            try:
                txtname = txt.name
                if txtname.endswith(".hivemap"):
                    treename = txtname[:-len(".hivemap")]
                    if treename.startswith("hivemaps/"):
                        treename = treename[len("hivemaps/"):]  # TODO

                    # Clear the existing NodeTree and replace it
                    if treename not in bpy.data.node_groups:
                        nodetree = bpy.data.node_groups.new(treename, "Hivemap")
                    else:
                        nodetree = bpy.data.node_groups[treename]
                    self._clear_nodetree(nodetree)
                    treename = nodetree.name
                    if treename not in self.blend_nodetree_managers:
                        ntm = BlendNodeTreeManager(self, treename, "Hivemap")
                        self.nodetrees.append((treename, "Hivemap"))
                        self.blend_nodetree_managers[treename] = ntm
                        ntm.start()
                    ntm = self.blend_nodetree_managers[treename]
                    hivemapstr = bpy.data.texts[txtname].as_string()
                    import spyder, Spyder

                    data = spyder.core.parse(hivemapstr)[1]
                    hivemap = Spyder.Hivemap.fromdict(data)
                    ntm.hivemapmanager._load(hivemap)
                    ntm.workermanager.sync_antennafoldstate()
            except:
                print("NODETREE IMPORT ERROR", txt.name)
                import traceback

                traceback.print_exc()

    def _load_workermaps(self):
        for txt in bpy.data.texts:
            if txt.as_string() == "<DELETED>": continue
            try:
                txtname = txt.name
                if txtname.endswith(".workermap"):
                    treename = txtname[:-len(".workermap")]
                    if treename.startswith("workermaps/"):
                        treename = treename[len("workermaps/"):] + "-worker"

                    if treename not in bpy.data.node_groups:
                        nodetree = bpy.data.node_groups.new(treename, "Workermap")
                    else:
                        nodetree = bpy.data.node_groups[treename]

                    treename = nodetree.name
                    if treename not in self.blend_nodetree_managers:
                        ntm = BlendNodeTreeManager(self, treename, "Workermap")
                        self.nodetrees.append((treename, "Workermap"))
                        self.blend_nodetree_managers[treename] = ntm
                        ntm.start()
                    ntm = self.blend_nodetree_managers[treename]
                    workermapstr = bpy.data.texts[txtname].as_string()
                    import spyder, Spyder

                    data = spyder.core.parse(workermapstr)[1]
                    workermap = Spyder.Workermap.fromdict(data)
                    ntm.workermapmanager._load(workermap)
            except:
                print("NODETREE IMPORT ERROR", txt.name)
                import traceback

                traceback.print_exc()

    def _load_spydermaps(self):
        for txt in bpy.data.texts:
            if txt.as_string() == "<DELETED>": continue
            try:
                txtname = txt.name
                if txtname.endswith(".spydermap"):
                    treename = txtname[:-len(".spydermap")]
                    if treename.startswith("spydermaps/"):
                        treename = treename[len("spydermaps/"):] + "-spyder"

                    if treename not in bpy.data.node_groups:
                        nodetree = bpy.data.node_groups.new(treename, "Spydermap")
                    else:
                        nodetree = bpy.data.node_groups[treename]

                    treename = nodetree.name
                    if treename not in self.blend_nodetree_managers:
                        ntm = BlendNodeTreeManager(self, treename, "Spydermap")
                        self.nodetrees.append((treename, "Spydermap"))
                        self.blend_nodetree_managers[treename] = ntm
                        ntm.start()
                    ntm = self.blend_nodetree_managers[treename]
                    import spyder, Spyder

                    spydermap = Spyder.Spydermap.fromfile("//" + txtname)
                    ntm.spydermapmanager._load(spydermap)
            except:
                print("NODETREE IMPORT ERROR", txt.name)
                import traceback

                traceback.print_exc()

    def activate(self):
        """
        Discovers all nodes
        #TODO: support re-discovery ("node sync"), also of Spyder models
        """
        self.discover_nodes_hivemap()
        self.discover_nodes_workermap()
        self.discover_nodes_spydermap()
        self._activated = True

    def blend_load(self):
        global _last_hive_level
        print("Hive loading hook", bpy.data.texts)
        if bpy.context.screen is not None:
            v = getattr(bpy.context.screen, "hive_level", None)
            if v is not None: v = int(v)
            _last_hive_level = v
        self.spyderhive_widget = BlenderOptionWidget(None, "", [])
        self.blend_nodetree_managers.clear()
        self.nodetrees = []
        self.activate()
        try:
            self._sync_text_to_nodetree()
        finally:
            self._loading = False
            self.blend_update()
        print("Hive loading hook DONE")

    def _blend_save(self):
        self._sync_nodetree_to_text()

    def blend_save(self, *args):
        print("Hive saving hook")
        # TODO what happens if this causes an exception, does this prevent the save? better take no chances..
        try:
            self._blend_save()
        except:
            import traceback

            traceback.print_exc()

    def get_nodetree_manager(self, finder, is_key=False):
        if not is_key:
            return self.blend_nodetree_managers[finder]

        return next((m for m in self.blend_nodetree_managers.values() if finder(m)))

    def game_pre(self):
        self._sync_nodetree_to_text()
        import os, sys

        self._olddir = os.getcwd()
        os.chdir(bpy.path.abspath("//"))

        import imp, bee.blendsupport, bee.blendsupport.blendblockimporter

        for hook in list(sys.path_hooks):
            if hasattr(hook, "__name__") and hook.__name__ == "blendblockimporter":
                sys.path_hooks.remove(hook)
        imp.reload(bee.blendsupport)
        imp.reload(bee.blendsupport.blendblockimporter)

        # clear Spyder file cache
        import inspect, spyder, Spyder

        inspect.getmodule(Spyder.Resource)._resources.clear()

    def game_post(self):
        import os, libcontext

        libcontext._contexts.clear()
        if self._olddir is not None:
            os.chdir(self._olddir)
            self._olddir = None

    def schedule(self, callback):
        self._scheduled.append(callback)

    def _do_schedule(self):
        while self._scheduled:
            callback = self._scheduled.pop(0)
            callback()

    def morph_state(self, current_profile, new_profile):
        for blend_nodetree_manager in self.blend_nodetree_managers.values():
            if blend_nodetree_manager.typ != "Hivemap": # TODO rename to type
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
        self.morph_state("default", "simplified")

    def unsimplify_all(self):
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
            if old_content != content and old_content != "<DELETED>":
                raise Exception("Cannot enable Hive system: Blender text block '%s' already exists" % block)

    main = [block for block, content in data if block.find("/") == -1 and block.endswith(".py")]
    if len(main) == 0:
        raise Exception("Could not find main script in default Blender project")

    if len(main) > 1:
        raise Exception("Multiple main script candidates in default Blender project: %s" % str(main))

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

            if old_content == content or old_content == "<DELETED>":
                try:
                    bpy.data.texts[block].remove()

                except:
                    bpy.data.texts[block].from_string("<DELETED>")

    del scene["__main__"]


def use_hive_get(context):
    if context.scene is None:
        return False

    if "__main__" in context.scene and context.scene["__main__"]:
        return 1

    else:
        return 0


def use_hive_set(context, value):
    global _last_hive_level

    if blendmanager is None:
        return

    if context.scene is None:
        return

    current = use_hive_get(context)
    if value == current:
        return

    if value:
        data = get_defaultproject_data()
        enable_hive(context.scene, data)
        _last_hive_level = 1

    else:
        disable_hive(context.scene)


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


