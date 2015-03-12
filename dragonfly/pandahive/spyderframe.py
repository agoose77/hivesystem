import Spyder, spyder, bee, libcontext
from bee import connect, Configure, ConfigureMultiple

from bee.spyderhive import spyderframe as spyderframe_orig, SpyderMethod, SpyderConverter


def create_material(mat):
    # only for color materials
    cf = Configure("scene")
    c = mat.color
    cf.create_material_COLOR(mat.pname, (c.r / 255.0, c.g / 255.0, c.b / 255.0))
    return cf


def show_entity(e):
    cf = Configure("scene")
    cf.start_block(mode="compile")
    cf.import_from_parentblock("materials")
    cf2 = e.objects.make_bee()
    cf3 = Configure("scene")
    cf3.render_block_SPYDER(entityname=e.entityname)
    cf3.end_block()
    return ConfigureMultiple(cf, cf2, cf3)


def show_objectlist3d(ol):
    cf = Configure("scene")
    cf.start_block()
    cf.import_from_parentblock("materials")
    configures = [cf]
    for o in ol:
        configures.append(o.make_bee())
    cf = Configure("scene")
    cf.end_block()
    configures.append(cf)
    return ConfigureMultiple(configures)


def show_objectgroup(og):
    cf = Configure("scene")
    cf.start_block(mode="compile")
    cf.import_from_parentblock("materials")
    cf2 = og.group.make_bee()
    cf3 = Configure("scene")
    cf3.render_block_SPYDER(axissystem=og.axis)
    cf3.end_block()
    return ConfigureMultiple(cf, cf2, cf3)


def show_multi_instance(mi):
    cf = Configure("scene")
    cf.start_block(mode="compile")
    cf.import_from_parentblock("materials")
    cf2 = mi.object.make_bee()
    cf3 = Configure("scene")
    for axis in mi.instances:
        cf3.render_block_SPYDER(axissystem=axis)
    cf3.end_block()
    return ConfigureMultiple(cf, cf2, cf3)


def show_multi_entity_instance(mi):
    cf = Configure("scene")
    cf.start_block(mode="compile")
    cf.import_from_parentblock("materials")
    cf2 = mi.object.make_bee()
    cf3 = Configure("scene")
    for axis, entityname in zip(mi.instances, mi.entitynames):
        cf3.render_block_SPYDER(axissystem=axis, entityname=entityname)
    cf3.end_block()
    return ConfigureMultiple(cf, cf2, cf3)


def show_object(obj):
    # only works for objects without face-specific materials
    #TODO: texturecoords

    cf = Configure("scene")
    cf.start_block()
    cf.import_from_parentblock("materials")
    vertices = [(c.x, c.y, c.z) for c in obj.vertices]
    faces = [tuple(f.vertices) for f in obj.faces]
    normals = []
    for f in obj.faces:
        normal = f.normal
        if f.normal is None:
            verts = [obj.vertices[n] for n in f.vertices]
            normal = spyder.tarantula.calc_normal(verts)
        normals.append((normal.x, normal.y, normal.z))
    if obj.lighting == "flat":
        normals = None  ###
        cf.create_mesh_per_face("mesh", vertices, faces, normals, None, None, None, obj.material)
    else:
        vertexnormals = []
        for vnr in range(len(vertices)):
            avgnormal = Spyder.Coordinate(0, 0, 0)
            for fnr, f in enumerate(faces):
                if vnr in f: avgnormal += normals[fnr]
            avgnormal = avgnormal.normalize()
            vertexnormals.append((avgnormal.x, avgnormal.y, avgnormal.z))
        cf.create_mesh_per_vertex("mesh", vertices, vertexnormals, None, None, faces, obj.material)

    cf.add_model_SPYDER("mesh", "model", axissystem=obj.axis)
    cf.end_block()
    return cf


def show_datablock(b):
    cf = Configure("scene")
    cf.start_block(b.pname, mode="datablock")
    cf.import_from_parentblock("materials")
    cf2 = b.object[0].make_bee()
    cf3 = Configure("scene")
    cf3.end_block()
    return ConfigureMultiple(cf, cf2, cf3)


def show_model(m):
    cf = Configure("scene")
    cf.start_block()
    cf.import_from_parentblock("materials")
    if m.meshformat != "egg": raise ValueError("panda can render only egg/bam meshes, not '%s'" % m.meshformat)
    cf.import_mesh_EGG(m.meshfilename)
    cf.add_model_SPYDER(modelname="model", axissystem=m.axis, material=m.material, entityname=m.entityname)
    cf.end_block()
    return cf


def show_actor(a):
    cf = Configure("scene")
    cf.start_block()
    cf.import_from_parentblock("materials")
    if a.meshformat != "egg": raise ValueError("panda can render only egg/bam meshes, not '%s'" % a.meshformat)
    cf.import_mesh_EGG(a.meshfilename)
    cf.add_actor_SPYDER(actorname="actor", axissystem=a.axis, material=a.material, entityname=a.entityname)
    for m in a.animations:
        # TODO check if every name is used only once
        if m.format != "egg": raise ValueError("panda can render only egg/bam meshes, not '%s'" % m.format)
        cf.import_mesh_EGG(m.filename)
        cf.add_animation(m.pname)
    cf.end_block()
    return cf


def show_actorclass(a):
    cf = Configure("scene")
    cf.start_block()
    cf.import_from_parentblock("materials")
    if a.meshformat != "egg": raise ValueError("panda can render only egg/bam meshes, not '%s'" % a.meshformat)
    cf.import_mesh_EGG(a.meshfilename)
    cf.add_actorclass_SPYDER(a.actorclassname, axissystem=a.axis, material=a.material)
    for m in a.animations:
        # TODO check if every name is used only once
        if m.format != "egg": raise ValueError("panda can render only egg/bam meshes, not '%s'" % m.format)
        cf.import_mesh_EGG(m.filename)
        cf.add_animation(m.pname)
    cf.end_block()
    return cf


def show_entityclass(e):
    cf = Configure("scene")
    cf.start_block(mode="compile")
    cf.import_from_parentblock("materials")
    cf2 = e.objects.make_bee()
    cf3 = Configure("scene")
    cf3.add_block_entityclass(entityclassname=e.entityclassname, material=e.material)
    cf3.end_block()
    return ConfigureMultiple(cf, cf2, cf3)


def world_to_namespace(w):
    return Spyder.Namespace(w.materials, w.objects)


from ..canvas import box2d
import bee


class parameters: pass


from bee.drone import dummydrone
from ..canvas import canvasargs
from libcontext.pluginclasses import plugin_single_required


def show_image(i):
    b = i.box
    box = box2d(b.x, b.y, b.sizex, b.sizey, b.mode)
    params = parameters()
    if i.transparency: params.transparency = True
    args = canvasargs(i.image, i.identifier, box, params)
    plugin = plugin_single_required(args)
    pattern = ("canvas", "draw", "init", ("object", "image"))
    d1 = dummydrone(plugindict={pattern: plugin})
    return d1.getinstance()


"""
def show_image(i):
  i1 = bee.init("canvas")
  b = i.box
  box = box2d(b.x,b.y,b.sizex,b.sizey,b.mode)
  params = parameters()
  if i.transparency: params.transparency = True
  i1.draw_image(StringValue(i.image),i.identifier,box,params)
  return i1
"""


def show_mousearea(i):
    i1 = bee.init("mousearea")
    b = i.box
    box = box2d(b.x, b.y, b.sizex, b.sizey, b.mode)
    i1.register(i.identifier, box)
    return i1


class spyderframe(spyderframe_orig):
    SpyderConverter("World3D", "Namespace", world_to_namespace)
    SpyderMethod("make_bee", "NewMaterial", create_material)
    SpyderMethod("make_bee", "Object3D", show_object)
    SpyderMethod("make_bee", "MultiInstance3D", show_multi_instance)
    SpyderMethod("make_bee", "MultiEntityInstance3D", show_multi_entity_instance)
    SpyderMethod("make_bee", "ObjectList3D", show_objectlist3d)
    SpyderMethod("make_bee", "ObjectGroup3D", show_objectgroup)
    SpyderMethod("make_bee", "Namespace", show_objectlist3d)
    SpyderMethod("make_bee", "DataBlock3D", show_datablock)
    SpyderMethod("make_bee", "Entity3D", show_entity)
    SpyderMethod("make_bee", "Model3D", show_model)
    SpyderMethod("make_bee", "Actor3D", show_actor)
    SpyderMethod("make_bee", "ActorClass3D", show_actorclass)
    SpyderMethod("make_bee", "EntityClass3D", show_entityclass)

    SpyderMethod("make_bee", "Image", show_image)
    SpyderMethod("make_bee", "MouseArea", show_mousearea)
  
