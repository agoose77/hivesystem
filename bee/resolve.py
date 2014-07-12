from .attribute import attribute
from .get_parameter import get_parameter


class resolvelist(list):
    pass


def resolve(v, parameters=None, prebuild=False, parent=None):
    if isinstance(v, resolvelist):
        return resolvelist([resolve(vv, parameters, prebuild, parent) for vv in v])

    elif isinstance(v, attribute):
        vv = v(parent, prebuild)
        if vv is v:
            if prebuild:
                return v

            if parent is None:
                raise TypeError("Cannot resolve attribute, parent has not been set")

            else:
                raise TypeError("Cannot resolve attribute: parent %s, prebuild %s" % (parent, prebuild))

        else:
            # return resolve(vv,parent,parameters,prebuild)
            return resolve(vv, parameters, prebuild)

    elif isinstance(v, get_parameter):
        if parent is None and parameters is None:
            raise TypeError("Cannot resolve get_parameter without parent or parameters")

        vv = v.get(parent, parameters)
        # return resolve(vv,parent,parameters,prebuild)
        return resolve(vv, parameters, prebuild, parent=parent)

    else:
        return v
