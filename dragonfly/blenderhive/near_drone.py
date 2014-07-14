import bee
import libcontext
from libcontext.socketclasses import *
from libcontext.pluginclasses import *

from collections import namedtuple

from .kdtree import kdtree as KDTree

PsuedoHitContact = namedtuple("HitContact", "distance position_a position_b node_a node_b")
PsuedoCollisionSphereShape = namedtuple("CollisiontSphere", "radius")
PsuedoCollisionResult = namedtuple("CollisionResult", "contacts")

try:
    import mathutils
except ImportError:
    pass
else:

    BoundVector = type("BoundVector", (mathutils.Vector,), {"__slots__": "data"})


class near_drone(bee.drone):

    """Fake collision API for the near sensor"""

    def __init__(self):
        self.entity_matrices = {}

    def enable(self):
        self.add_listener("trigger", self.update_distances, "tick", priority=9)

    def set_get_entity_names(self, function):
        self.get_entity_names = function

    def create_sphere(self, radius, is_ghost):
        return PsuedoCollisionSphereShape(radius)

    def contact_test(self, position, node, filter_func=None):
        contacts = []

        source_position = mathutils.Vector((position.x, position.y, position.z))
        for distance, node in self.kd_tree.nn_range_search(source_position, node.radius):
            position = node.position
            entity_name_ = position.data
            if filter_func is not None:
                if not filter_func(entity_name_):
                    continue

            contact = PsuedoHitContact(distance, position, position, node, entity_name_)
            contacts.append(contact)

        return PsuedoCollisionResult(contacts)

    def update_distances(self):
        entities = list(self.get_entity_names())

        points = []
        for index, entity_name in enumerate(entities):
            try:
                matrix = self.entity_matrices[entity_name]

            except KeyError:
                matrix = self.entity_matrices[entity_name] = self.get_entity_matrix(entity_name).get_proxy("Blender")

            point = BoundVector(matrix.worldPosition)
            point.data = entity_name
            points.append(point)

        kd_tree = KDTree(points, 3)

        self.kd_tree = kd_tree

    def set_add_listener(self, func):
        self.add_listener = func

    def set_get_entity_matrix(self, func):
        self.get_entity_matrix = func

    def place(self):
        libcontext.plugin(("collision", "contact_test"), plugin_supplier(self.contact_test))
        libcontext.plugin(("collision", "create_node", "sphere"), plugin_supplier(self.create_sphere))
        libcontext.socket(("entity", "names"), socket_single_required(self.set_get_entity_names))
        libcontext.socket(("entity", "matrix"), socket_single_required(self.set_get_entity_matrix))

        # Add a high-priority deactivate() listener on every tick
        libcontext.socket(("evin", "add_listener"), socket_single_required(self.set_add_listener))
        libcontext.plugin(("bee", "init"), plugin_single_required(self.enable))