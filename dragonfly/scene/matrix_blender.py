class blender_wraps_blender(object):
    _matrixview = None

    def __init__(self, wrapped):
        self._wrapped = wrapped

    def __getattr__(self, attr):
        return getattr(self._wrapped, attr)

    def set_matrixview(self, matrix_view):
        self._matrixview = matrix_view

    def commit(self):
        if self._matrixview is not None:
            self._matrixview(self._wrapped)


def axissystem_to_blender(a, blenderobject):
    import mathutils

    blenderobject.localPosition = mathutils.Vector([float(a.origin.x), float(a.origin.y), float(a.origin.z)])
    # blenderobject.position = mathutils.Vector([float(a.origin.x),float(a.origin.y),float(a.origin.z)])

    """
    blenderobject.localOrientation = mathutils.Matrix([[float(a.x.x),float(a.x.y),float(a.x.z)],
                                                      [float(a.y.x),float(a.y.y),float(a.y.z)],
                                                      [float(a.z.x),float(a.z.y),float(a.z.z)]])
    """
    """
    blenderobject.orientation =     mathutils.Matrix([[float(a.x.x),float(a.x.y),float(a.x.z)],
                                                      [float(a.y.x),float(a.y.y),float(a.y.z)],
                                                      [float(a.z.x),float(a.z.y),float(a.z.z)]])
    """
    blenderobject.localOrientation = mathutils.Matrix([[float(a.x.x), float(a.y.x), float(a.z.x)],
                                                       [float(a.x.y), float(a.y.y), float(a.z.y)],
                                                       [float(a.x.z), float(a.y.z), float(a.z.z)]])
    """
    blenderobject.orientation =     mathutils.Matrix([[float(a.x.x),float(a.y.x),float(a.z.x)],
                                                      [float(a.x.y),float(a.y.y),float(a.z.y)],
                                                      [float(a.x.z),float(a.y.z),float(a.z.z)]])
    """


def nodepath_to_blender(a, blenderobject):
    import mathutils

    blenderobject.localPosition = mathutils.Vector(a[12:15])
    blenderobject.localOrientation = mathutils.Matrix([[a[0], a[4], a[8]],
                                                       [a[1], a[5], a[9]],
                                                       [a[2], a[6], a[10]],
    ]
    )
