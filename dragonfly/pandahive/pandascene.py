# ##
# actorname is for INTERNAL reference (in a block, during scene creation to add animations)
# entityname is for EXTERNAL reference (to retrieve the actor/node later)
###

import bee, libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *

try:
    from direct.actor.Actor import Actor
    from panda3d.core import GeomVertexFormat, GeomVertexData
    from panda3d.core import Geom, GeomTriangles, GeomVertexWriter, GeomNode
    from panda3d.core import Vec3, Vec4, Point3, NodePath, Mat4, Material, VBase4
    import panda3d
except ImportError:
    panda3d = None

"""
axis = [a.x.x,a.x.y,a.x.z,0,
        a.y.x,a.y.y,a.y.z,0,
        a.z.x,a.z.y,a.z.z,0,
        a.origin.x, a.origin.y, a.origin.z, 1]
"""


def get_matrix4(p, x, y, z):
    return Mat4(x[0], x[1], x[2], 0, y[0], y[1], y[2], 0, z[0], z[1], z[2], 0, p[0], p[1], p[2], 1)


class pandaresource(object):
    def __init__(self):
        self.loaded = False
        self.node = None

    def load(self):
        raise Exception("Must be overridden")

    def render_MATRIX(self, matrix=None, material=None):
        if matrix is not None: pos, x, y, z = matrix
        if self.loaded == False:
            self.load()
        if matrix is not None:
            mat = get_matrix4(pos, x, y, z)
            self.node.setMat(mat)
        if material is not None:
            self.node.setMaterial(material, priority=1)
        return self.node

    def render_SPYDER(self, axissystem=None, material=None):
        if axissystem is None: return self.render_MATRIX(material=material)
        a = axissystem
        p = a.origin.x, a.origin.y, a.origin.z
        x = a.x.x, a.x.y, a.x.z
        y = a.y.x, a.y.y, a.y.z
        z = a.z.x, a.z.y, a.z.z
        return self.render_MATRIX((p, x, y, z), material=material)


class pandaentityclass(pandaresource):

    def __init__(self, node):
        self._node = node

    def load(self):
        self.node = NodePath("")
        self._node.instanceTo(self.node)
        self.loaded = False


class eggmodel(pandaresource):
    def __init__(self, eggname, load_models):
        self.eggname = eggname
        self.load_models = load_models
        pandaresource.__init__(self)

    def set_entityname(self, entityname):
        self.entityname = entityname

    def load(self):
        if panda3d is None: raise ImportError("Cannot locate Panda3D")
        self.node = NodePath("")
        self.load_models.append((self.entityname, self.eggname, self.node))
        self.loaded = True


class eggactor(pandaresource):
    def __init__(self, eggname, load_actors):
        self.eggname = eggname
        self.load_actors = load_actors
        self.animations = {}
        pandaresource.__init__(self)

    def set_entityname(self, entityname):
        self.entityname = entityname

    def load(self):
        if panda3d is None: raise ImportError("Cannot locate Panda3D")
        self.node = NodePath("")
        self.loaded = False  #for every new actor, re-load the model
        self.load_actors.append((self.entityname, self.eggname, self.node, self.animations))
        self.used = False


class eggactorclass(pandaresource):
    def __init__(self, eggname):
        self.eggname = eggname
        self.animations = {}
        pandaresource.__init__(self)

    def load(self):
        if panda3d is None: raise ImportError("Cannot locate Panda3D")
        self.actor = Actor(self.eggname, self.animations)
        self.node = self.actor
        if self.material is not None: self.node.setMaterial(self.material, priority=1)
        self.loaded = False  #for every new use, re-load the Actor


class eggmodelclass(pandaresource):
    def __init__(self, eggname):
        self.eggname = eggname
        pandaresource.__init__(self)

    def load_model(self, modelloader, material):
        self.model = modelloader(self.eggname)
        if material is not None:
            self.model.setMaterial(material, priority=1)

    def load(self):
        if panda3d is None: raise ImportError("Cannot locate Panda3D")
        self.node = NodePath("")
        self.model.instanceTo(self.node)
        self.loaded = False  #for every new use, re-instance to self.node


def make_geom(vertices, normals, colors, texcoords):
    if panda3d is None: raise ImportError("Cannot locate Panda3D")
    format = "V3"
    if normals is not None:
        assert len(normals) == len(vertices)
        format += "n3"

    if colors is not None:
        assert len(colors) == len(vertices)
        format += "cp"

    if texcoords is not None:
        assert len(texcoords) == len(vertices)
        format += "t2"
    format = getattr(GeomVertexFormat, "get" + format)()
    vdata = GeomVertexData("", format, Geom.UHStatic)

    v_vertex = GeomVertexWriter(vdata, 'vertex')
    if normals is not None: v_normals = GeomVertexWriter(vdata, 'normal')
    if colors is not None: v_colors = GeomVertexWriter(vdata, 'color')
    if texcoords is not None: v_texcoords = GeomVertexWriter(vdata, 'texcoord')

    for n in range(len(vertices)):
        v_vertex.addData3f(*vertices[n])
        if normals is not None: v_normals.addData3f(*normals[n])
        if colors is not None: v_colors.addData4f(*colors[n])
        if texcoords is not None: v_texcoords.addData2f(*texcoords[n])

    return Geom(vdata)


class manualmodel_per_vertex(pandaresource):
    #normals, colors, texcoords per vertex
    def __init__(self, name, vertices, normals, colors, texcoords, faces, material):
        pandaresource.__init__(self)
        self.name = name
        self.vertices = vertices
        self.normals = normals
        self.colors = colors
        self.texcoords = texcoords
        self.faces = faces
        self.material = material

    def set_entityname(self, entityname):
        self.entityname = entityname

    def load(self):
        if panda3d is None: raise ImportError("Cannot locate Panda3D")
        #KLUDGE
        if self.material is not None and self.colors == None:
            col = self.material.getAmbient()
            col = (col[0] / col[3], col[1] / col[3], col[2] / col[3], 1.0)
            self.colors = (col,) * len(self.vertices)
        #/KLUDGE
        geom = make_geom(self.vertices, self.normals, self.colors, self.texcoords)
        prim = GeomTriangles(Geom.UHStatic)
        for face in self.faces:
            #TODO: proper tesselation! the current one only works for convex faces
            first = face[0]
            curr = face[1]
            for v in face[2:]:
                prim.addVertex(curr)
                prim.addVertex(v)
                prim.addVertex(first)
                curr = v
        prim.closePrimitive()
        geom.addPrimitive(prim)
        node = GeomNode(self.name)
        node.addGeom(geom)

        self.node = NodePath(node)
        self.node.setTwoSided(True)
        if self.material is not None: self.node.setMaterial(self.material, priority=1)
        self.loaded = True


class manualmodel_per_face(pandaresource):
    #normals, facecolors: one per face
    #fvcolors, texcoordinates: one per facevertex
    def __init__(self, name, vertices, faces, normals, facecolors, fvcolors, texcoords, material):
        pandaresource.__init__(self)
        self.name = name
        self.vertices = vertices
        self.faces = faces
        self.normals = normals
        self.facecolors = facecolors
        self.fvcolors = fvcolors
        self.material = material
        assert self.facecolors == None or self.fvcolors == None
        self.texcoords = texcoords
        if self.normals is not None:
            assert len(self.normals) == len(self.faces)
        if self.facecolors is not None:
            assert len(self.facecolors) == len(self.faces)
        if self.fvcolors is not None:
            assert len(self.fvcolors) == len(self.faces)
            for facecolors, facevertices in zip(self.fvcolors, self.faces):
                assert len(facecolors) == len(facevertices)
        if self.texcoords is not None:
            assert len(self.texcoords) == len(self.faces)
            for facetexcoords, facevertices in zip(self.texcoords, self.faces):
                assert len(facetexcoords) == len(facevertices)

    def set_entityname(self, entityname):
        self.entityname = entityname

    def load(self):
        if panda3d is None: raise ImportError("Cannot locate Panda3D")
        node = GeomNode(self.name)
        for n in range(len(self.faces)):
            facevertices = self.faces[n]
            vertices = [self.vertices[v] for v in facevertices]
            normals = None
            if self.normals is not None:
                normals = (self.normals[n],) * len(facevertices)
            colors = None
            if self.facecolors is not None:
                colors = (self.facecolors[n],) * len(facevertices)
            elif self.fvcolors is not None:
                colors = self.fvcolors[n]
            texcoords = None
            if self.texcoords is not None:
                texcoords = self.texcoords[n]

            #KLUDGE
            if self.material is not None and colors == None:
                col = self.material.getAmbient()
                col = (col[0] / col[3], col[1] / col[3], col[2] / col[3], 1.0)
                colors = (col,) * len(vertices)
            #/KLUDGE

            geom = make_geom(vertices, normals, colors, texcoords)
            prim = GeomTriangles(Geom.UHStatic)

            #TODO: proper tesselation! the current one only works for convex faces
            curr = 1
            for v in range(2, len(facevertices)):
                prim.addVertex(curr)
                prim.addVertex(v)
                prim.addVertex(0)
                curr = v
            prim.closePrimitive()
            geom.addPrimitive(prim)
            node.addGeom(geom)
        self.node = NodePath(node)
        self.node.setTwoSided(True)
        if self.material is not None:
            self.node.setMaterial(self.material, priority=1)
        self.loaded = True


class renderblock(object):
    def __init__(self, mode, static):
        self.mode = mode
        self.static = static  #ignore for Panda?
        ##definitions
        self.materials = {}  #material definitions
        self.meshes = {}  #mesh imports
        self.manualmodels = {}  #mesh definitions
        #self.models = {}    #model definitions
        self.actors = {}  #actor definitions; only in non-static blocks
        self.childblocks = {}
        self.lastblock = None
        self.lastmesh = None  #in Panda, this is a string (reload the mesh for a new copy!)
        self.lastactor = None  #in Panda, this is a string (reload the mesh for a new copy!)
        self.commands = []  #commands are eager in dragonfly.panda => implemented as list of NodePaths
        #node
        self.node = None
        self.children = 0
        #implemented as NodePath in dragonfly.panda

    def __str__(self):
        ret = "renderblock %s\n" % id(self)
        for a in sorted(self.__dict__.keys()):
            ret += "%s: %s\n" % (a, self.__dict__[a])
        return ret


class pandarenderblock(renderblock, pandaresource):
    def __init__(self, mode, static):
        renderblock.__init__(self, mode, static)
        pandaresource.__init__(self)
        if panda3d is None: raise ImportError("Cannot locate Panda3D")
        self.render = NodePath("")

    def load(self):
        if panda3d is None: raise ImportError("Cannot locate Panda3D")
        self.node = NodePath("")
        if not self.render.hasParent():
            self.render.reparentTo(self.node)
        else:
            self.render.instanceTo(self.node)


class pandascene(bee.drone):
    def __init__(self):
        self.blocks = [pandarenderblock(mode="standard", static=None)]
        self.load_models = []
        self.load_actors = []
        self.block_entities = []
        self.actorclasses = []
        self.modelclasses = []
        self.entityclasses = []

    def init(self):
        if len(self.blocks) > 1: raise Exception
        if panda3d is None: raise ImportError("Cannot locate Panda3D")

        self.blocks[0].render.reparentTo(self.get_parent_render())
        for entityname, eggname, node in self.load_models:
            model = self.get_loader().loadModel(eggname)
            model.setMat(node.getMat())
            material = node.getMaterial()
            if material is not None:
                model.setMaterial(material, priority=1)
            if entityname is not None:
                self.entity_register((entityname, NodePath(model)))
            model.reparentTo(node.getParent())
            node.detachNode()

        for entityname, eggname, node, animations in self.load_actors:
            actor = Actor(eggname, animations)
            actor.setMat(node.getMat())
            material = node.getMaterial()
            if material is not None:
                actor.setMaterial(material, priority=1)
            if entityname is not None:
                self.actor_register((entityname, actor))
                self.entity_register((entityname, NodePath(actor)))
            actor.reparentTo(node.getParent())
            node.detachNode()

        for entityname, blocknode in self.block_entities:
            self.entity_register((entityname, blocknode))

        for actorclassname, actor, material, nodepath in self.actorclasses:
            actor.material = material
            actor.load()  #just to test if the egg files exist
            self.actorclass_register((actorclassname, actor, nodepath))
            self.entityclass_register((actorclassname, actor, nodepath))

        for modelclassname, model, material, nodepath in self.modelclasses:
            model.load_model(self.get_loader().loadModel, material)
            self.entityclass_register((modelclassname, model, nodepath))

        for entityclassname, entityclass, nodepath in self.entityclasses:
            self.entityclass_register((entityclassname, entityclass, nodepath))

    def _set_render(self, get_render):
        self.get_parent_render = get_render

    def _set_loader(self, get_loader):
        self.get_loader = get_loader

    def _set_actor_register(self, actor_register):
        self.actor_register = actor_register

    def _set_entity_register(self, entity_register):
        self.entity_register = entity_register

    def _set_actorclass_register(self, actorclass_register):
        self.actorclass_register = actorclass_register

    def _set_entityclass_register(self, entityclass_register):
        self.entityclass_register = entityclass_register

    def start_block(self, name=None, mode="standard", static=None):
        newblock = pandarenderblock(mode, static)
        self.blocks[-1].lastblock = newblock
        if name is not None: self.blocks[-1].childblocks[name] = newblock
        self.blocks.append(newblock)

    def import_from_parentblock(self, what_to_import):
        assert len(self.blocks) > 1
        assert what_to_import in ("materials", "objects", "blocks")
        currblock = self.blocks[-1]
        parentblock = self.blocks[-2]
        if what_to_import == "materials":
            currblock.materials.update(parentblock.materials)
        elif what_to_import == "objects":
            currblock.manualmodels.update(parentblock.manualmodels)
            currblock.meshes.update(parentblock.meshes)
            currblock.models.update(parentblock.models)
            currblock.actors.update(parentblock.actors)
        elif what_to_import == "blocks":
            for bname in parentblock.childblocks:
                b = parentblock.childblocks[bname]
                if b is not currblock: currblock.childblocks[bname] = b

    def end_block(self):
        if len(self.blocks) == 1: raise Exception
        b = self.blocks[-1]
        self.blocks.pop()
        currblock = self.blocks[-1]
        if currblock.mode in ("standard", "datablock") and b.mode != "datablock":
            #TODO: eliminate node if only one child
            node = b.render_MATRIX()
            node.reparentTo(currblock.render)
        currblock.lastblock = b

    def import_mesh_EGG(self, eggname, meshname=None):
        #m = (eggmodel(eggname, self.load_models), eggactor(eggname, self.load_actors))  # This would be the Ogre way
        #if meshname is not None:
        #self.blocks[-1].meshes[meshname] = m This would be the Ogre way...
        if meshname is not None:
            self.blocks[-1].meshes[meshname] = eggname
        #self.blocks[-1].lastmesh = m  This would be the Ogre way...
        self.blocks[-1].lastmesh = eggname

    import_mesh = import_mesh_EGG

    def create_mesh_per_vertex(self, meshname, vertices, normals, colors, texcoords, faces, material):
        currblock = self.blocks[-1]
        if material is not None:
            material = currblock.materials[material]
        m = manualmodel_per_vertex(meshname, vertices, normals, colors, texcoords, faces, material)
        m.load()
        currblock.manualmodels[meshname] = m
        currblock.meshes[meshname] = meshname
        currblock.lastmesh = meshname

    def create_mesh_per_face(self, meshname, vertices, faces, normals, facecolors, fvcolors, texcoords, material):
        currblock = self.blocks[-1]
        if material is not None:
            material = currblock.materials[material]
        m = manualmodel_per_face(meshname, vertices, faces, normals, facecolors, fvcolors, texcoords, material)
        m.load()
        currblock.manualmodels[meshname] = m
        currblock.meshes[meshname] = meshname
        currblock.lastmesh = meshname

    #def import_material_XXX(materialname, import_as): DOES NOT EXIST in Panda3D
    #  pass
    def create_material_COLOR(self, materialname, color):
        if panda3d is None: raise ImportError("Cannot locate Panda3D")

        currblock = self.blocks[-1]
        assert materialname not in currblock.materials
        mat = Material()
        mat.setAmbient(VBase4(color[0], color[1], color[2], 1))
        mat.setDiffuse(VBase4(color[0], color[1], color[2], 1))
        currblock.materials[materialname] = mat

    def _get_mesh_model(self, meshname):
        currblock = self.blocks[-1]
        if meshname is None:
            assert currblock.lastmesh is not None
            #model = currblock.lastmesh[0] #this would be the Ogre way...
            meshname = currblock.lastmesh
        else:
            #model = currblock.meshes[meshname][0] #this would be the Ogre way...
            pass
        #return model #this would be the Ogre way...

        if meshname in currblock.manualmodels:
            return currblock.manualmodels[meshname]
        else:
            return eggmodel(meshname, self.load_models)

    def add_modelclass_SPYDER(self, modelclassname, meshname=None, material=None, axissystem=None):
        nodepath = None
        if axissystem is not None:
            if panda3d is None: raise ImportError("Cannot locate Panda3D")
            nodepath = NodePath("")
            a = axissystem
            p = a.origin.x, a.origin.y, a.origin.z
            x = a.x.x, a.x.y, a.x.z
            y = a.y.x, a.y.y, a.y.z
            z = a.z.x, a.z.y, a.z.z
            nodepath.setMat(get_matrix4(p, x, y, z))
        self.add_modelclass(modelclassname, meshname, material, nodepath)

    def add_modelclass_MATRIX(self, modelclassname, meshname=None, material=None, matrix=None):
        nodepath = None
        if matrix is not None:
            if panda3d is None: raise ImportError("Cannot locate Panda3D")
            nodepath = NodePath("")
            p, x, y, z = matrix
            nodepath.setMat(get_matrix4(p, x, y, z))
        self.add_modelclass(modelclassname, meshname, material, nodepath)

    def add_modelclass(self, modelclassname, meshname=None, material=None, nodepath=None):
        currblock = self.blocks[-1]
        if meshname is None:
            assert currblock.lastmesh is not None
            meshname = currblock.lastmesh

        if meshname in currblock.manualmodels:
            manualmodel = currblock.manualmodels[meshname]
            manualmodel.material = material
            manualmodel.loaded = False
            manualmodel.load()
            entityclass = pandaentityclass(manualmodel.node)
            self.entityclasses.append((modelclassname, entityclass, nodepath))
            #TODO fix variable
            manualmodel.material = mat
        else:
            model = eggmodelclass(meshname)
            self.modelclasses.append((modelclassname, model, material, nodepath))

    def add_model_MATRIX(self, meshname=None, modelname=None, material=None, matrix=None, entityname=None):
        model = self._get_mesh_model(meshname)
        model.set_entityname(entityname)
        currblock = self.blocks[-1]
        if material is not None:
            material = currblock.materials[material]
        modelnode = model.render_MATRIX(matrix, material)
        modelnode.reparentTo(currblock.render)
        currblock.children += 1

    def add_model_SPYDER(self, meshname=None, modelname=None, material=None, axissystem=None, entityname=None):
        model = self._get_mesh_model(meshname)
        model.set_entityname(entityname)
        currblock = self.blocks[-1]
        if material is not None:
            material = currblock.materials[material]
        modelnode = model.render_SPYDER(axissystem, material)
        modelnode.reparentTo(currblock.render)
        currblock.children += 1

    def _get_mesh_actor(self, meshname, actorname):
        currblock = self.blocks[-1]
        if meshname is None:
            assert currblock.lastmesh is not None
            #actor = currblock.lastmesh[1] #This would be the Ogre way
            meshname = currblock.lastmesh
        else:
            #actor = currblock.meshes[meshname][1] #This would be the Ogre way
            pass
        assert meshname not in currblock.manualmodels
        actor = eggactor(meshname, self.load_actors)  #Panda way
        currblock.lastactor = actor
        if actorname is not None: currblock.actors[actorname] = actor
        return actor

    def add_actorclass_SPYDER(self, actorclassname, meshname=None, material=None, axissystem=None):
        nodepath = None
        if axissystem is not None:
            if panda3d is None: raise ImportError("Cannot locate Panda3D")
            nodepath = NodePath("")
            a = axissystem
            p = a.origin.x, a.origin.y, a.origin.z
            x = a.x.x, a.x.y, a.x.z
            y = a.y.x, a.y.y, a.y.z
            z = a.z.x, a.z.y, a.z.z
            nodepath.setMat(get_matrix4(p, x, y, z))
        self.add_actorclass(actorclassname, meshname, material, nodepath)

    def add_actorclass_MATRIX(self, actorclassname, meshname=None, material=None, matrix=None):
        nodepath = None
        if matrix is not None:
            if panda3d is None: raise ImportError("Cannot locate Panda3D")
            nodepath = NodePath("")
            p, x, y, z = matrix
            nodepath.setMat(get_matrix4(p, x, y, z))
        self.add_actorclass(actorclassname, meshname, material, nodepath)

    def add_actorclass(self, actorclassname, meshname=None, material=None, nodepath=None):
        currblock = self.blocks[-1]
        if meshname is None:
            assert currblock.lastmesh is not None
            #actor = currblock.lastmesh[1] #This would be the Ogre way
            meshname = currblock.lastmesh
        else:
            #actor = currblock.meshes[meshname][1] #This would be the Ogre way
            pass
        assert meshname not in currblock.manualmodels
        actorclass = eggactorclass(meshname)
        actorclass.material = material
        currblock.lastactor = actorclass
        if actorclassname is not None: currblock.actors[actorclassname] = actorclass

        if material is not None:
            material = currblock.materials[material]
        self.actorclasses.append((actorclassname, actorclass, material, nodepath))

    def add_actor_MATRIX(self, actorname=None, meshname=None, material=None, matrix=None, entityname=None):
        actor = self._get_mesh_actor(meshname, actorname)
        actor.set_entityname(entityname)
        currblock = self.blocks[-1]
        if material is not None:
            material = currblock.materials[material]
        actornode = actor.render_MATRIX(matrix, material)
        actornode.reparentTo(currblock.render)
        currblock.children += 1

    def add_actor_SPYDER(self, actorname=None, meshname=None, material=None, axissystem=None, entityname=None):
        actor = self._get_mesh_actor(meshname, actorname)
        actor.set_entityname(entityname)
        currblock = self.blocks[-1]
        if material is not None:
            material = currblock.materials[material]
        actornode = actor.render_SPYDER(axissystem, material)
        actornode.reparentTo(currblock.render)
        currblock.children += 1

    def _get_actor(self, actorname):
        currblock = self.blocks[-1]
        if actorname is None:
            assert currblock.lastactor is not None
            actor = currblock.lastactor
        else:
            actor = currblock.actors[actorname]
        return actor

    def add_animation(self, animation, eggname=None, actorname=None):
        currblock = self.blocks[-1]
        if eggname is None:
            assert currblock.lastmesh is not None
            eggname = currblock.lastmesh
        actor = self._get_actor(actorname)
        actor.animations[animation] = eggname

    def _get_block(self, blockname):
        currblock = self.blocks[-1]
        if blockname == None:
            assert currblock.lastblock is not None
            return currblock.lastblock
        else:
            assert blockname in currblock.childblocks
            return currblock.childblocks[blockname]

    def render_block_MATRIX(self, blockname=None, matrix=None, entityname=None, material=None):
        currblock = self.blocks[-1]
        b = self._get_block(blockname)
        node = b.render_MATRIX(matrix, material=material)
        node.reparentTo(currblock.render)
        if entityname is not None:
            self.block_entities.append((entityname, node, modelclass))

    def render_block_SPYDER(self, blockname=None, axissystem=None, entityname=None, material=None):
        currblock = self.blocks[-1]
        b = self._get_block(blockname)
        node = b.render_SPYDER(axissystem, material=material)
        node.reparentTo(currblock.render)
        if entityname is not None:
            self.block_entities.append((entityname, node))

    def add_block_entityclass_SPYDER(self, entityclassname, blockname=None, material=None, axisystem=None):
        nodepath = None
        if axissystem is not None:
            if panda3d is None: raise ImportError("Cannot locate Panda3D")
            nodepath = NodePath("")
            a = axissystem
            p = a.origin.x, a.origin.y, a.origin.z
            x = a.x.x, a.x.y, a.x.z
            y = a.y.x, a.y.y, a.y.z
            z = a.z.x, a.z.y, a.z.z
            nodepath.setMat(get_matrix4(p, x, y, z))
        self.add_block_entityclass(entityclassname, blockname, material, nodepath)

    def add_block_entityclass_MATRIX(self, entityclassname, blockname=None, material=None, matrix=None):
        nodepath = None
        if matrix is not None:
            if panda3d is None: raise ImportError("Cannot locate Panda3D")
            nodepath = NodePath("")
            p, x, y, z = matrix
            nodepath.setMat(get_matrix4(p, x, y, z))
        self.add_block_entityclass(entityclassname, blockname, material, nodepath)

    def add_block_entityclass(self, entityclassname, blockname=None, material=None, nodepath=None):
        b = self._get_block(blockname)
        node = b.render_MATRIX(material=material)
        self.entityclasses.append((entityclassname, pandaentityclass(node), nodepath))

    def place(self):
        if panda3d is None:
            raise ImportError("Cannot locate Panda3D")

        libcontext.plugin("startupfunction", plugin_single_required(self.init))
        libcontext.socket(("panda", "noderoot", "render"), socket_single_required(self._set_render))
        libcontext.socket(("panda", "noderoot", "loader"), socket_single_required(self._set_loader))
        libcontext.socket(("panda", "actor-register"), socket_single_required(self._set_actor_register))
        libcontext.socket(("panda", "entity-register"), socket_single_required(self._set_entity_register))
        libcontext.socket(("panda", "actorclass-register"), socket_single_required(self._set_actorclass_register))
        libcontext.socket(("panda", "entityclass-register"), socket_single_required(self._set_entityclass_register))

