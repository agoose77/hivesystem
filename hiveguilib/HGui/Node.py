from __future__ import print_function, absolute_import

# TODO named tuple these things!

class Connection(object):
    def __init__(self,
                 start_node,  # id!
                 start_attribute,
                 end_node,  #id!
                 end_attribute,
                 interpoints):
        self.start_node = start_node
        self.start_attribute = start_attribute
        self.end_node = end_node
        self.end_attribute = end_attribute
        self.interpoints = interpoints

    def __eq__(self, other):
        assert isinstance(other, self.__class__)
        return self.to_tuple() == other.to_tuple()

    def __hash__(self):
        return hash(self.to_tuple())

    def __str__(self):
        output_string = """Connection (\n\t"%s", "%s", \n\t"%s", "%s",\n\t[%s]\n)""" % (
            self.start_node, self.start_attribute,
            self.end_node, self.end_attribute,
            ", ".join(["(%d,%d)" % (x, y) for x, y in self.interpoints])
        )
        return output_string

    def to_tuple(self):
        return self.start_node, self.start_attribute, self.end_node, self.end_attribute, self.interpoints


class Hook(object):
    def __init__(self,
                 mode,
                 type,
                 tooltip=None,
                 visible=True
    ):
        assert mode in ("push", "pull")
        self.mode = mode
        self.type = type
        self.tooltip = tooltip
        assert visible in (True, False)
        self.visible = visible

    def __copy__(self):
        return Hook(self.mode, self.type, self.tooltip, self.visible)


class Attribute(object):

    def __init__(self, name, inhook=None, outhook=None, type=None, value=None, label=None, tooltip=None,  visible=True):
        self.name = name
        assert inhook is None or isinstance(inhook, Hook)
        self.inhook = inhook
        assert outhook is None or isinstance(outhook, Hook)
        self.outhook = outhook
        self.type = type
        self.value = value
        self.label = label
        self.tooltip = tooltip
        self.visible = visible

    def __copy__(self):
        import copy

        inhook = copy.copy(self.inhook)
        outhook = copy.copy(self.outhook)
        return Attribute(
            self.name, inhook, outhook,
            self.type, self.value,
            self.label, self.tooltip, self.visible
        )


class Node(object):

    def __init__(self, name, position, attributes, tooltip=None, empty=False):
        self.name = name
        self.position = position
        self.attributes = attributes
        for attribute in attributes:
            assert isinstance(attribute, Attribute)
        self.tooltip = tooltip
        self.empty = empty

    def get_attribute(self, attribute_name):
        matching_attributes = [a for a in self.attributes if a.name == attribute_name]
        if len(matching_attributes) == 0:
            raise NameError("Node '%s' has no attribute named '%s'" % (self.name, attribute_name))
        elif len(matching_attributes) > 1:
            raise NameError("Node '%s' has %d attributes named '%s'" % (self.name, len(matching_attributes),
                                                                        attribute_name))
        return matching_attributes[0]

    def __copy__(self):
        import copy
        attribs = [copy.copy(a) for a in self.attributes]
        return Node(self.name, self.position, attribs, self.tooltip)
