import sys

is_python2 = (sys.version_info[0] == 2)
is_python3 = (sys.version_info[0] == 3)

if is_python2:
    Type = type
    Object = object

elif is_python3:
    cache = set()

    class Type(type):

        """Custom metaclass to handle Python 2 and Python 3 syntax differences.

        Supports __metaclass__ syntax, provided metaclass derives from Type
        """

        def __new__(metacls, name, bases, cls_dict, **kargs):
            meta = type
            modified_cache = False

            if metacls not in cache:
                cache.add(metacls)
                modified_cache = True
                if "__metaclass__" in cls_dict:
                    meta = cls_dict["__metaclass__"]

                else:
                    for base_cls in bases:
                        if hasattr(base_cls, "__metaclass__"):
                            meta = base_cls.__metaclass__
                            break

            # Default state, we are taking the place of type
            if meta is type:
                returned_cls = super().__new__(metacls, name, bases, cls_dict, **kargs)

            # We allow ourselves to call type
            elif meta is Type:
                returned_cls = type(name, bases, cls_dict)

            # Inherited metaclass must first be called
            else:
                returned_cls = meta.__new__(meta, name, bases, cls_dict, **kargs)

            returned_cls.__metaclass__ = meta

            if modified_cache:
                cache.remove(metacls)

            return returned_cls

    class Object(metaclass=Type):
        """Base class for Python3 objects

        Provides compatibility with explicit Python2 inheritance of object
        """