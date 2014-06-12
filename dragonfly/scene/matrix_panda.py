import math


class dummynodepath(object):
    def __init__(self, mat):
        self._mat = mat

    def setHpr(self, h, p, r):
        import mathutils

        hpr = h, p, r
        hpr_rad = [math.radians(v) for v in hpr]
        eul = mathutils.Euler(hpr_rad, 'ZXY')
        mat = eul.to_matrix()
        x = mat[0]
        y = mat[1]
        z = mat[2]
        p = self._mat[12:15]
        self._mat = _blender_to_nodepath(x, y, z, p)._mat

    def getHpr(self):
        import mathutils

        a = self._mat
        rot = mathutils.Matrix(
            [a[0], a[4], a[8]],
            [a[1], a[5], a[9]],
            [a[2], a[6], a[10]],
        )
        eul = rot.to_euler('ZXY')
        hpr = eul[2], eul[0], eul[1]
        hpr = [rad / math.pi * 180 for rad in hpr]
        return tuple(hpr)

    def setH(self, h):
        hpr = self.getHpr()
        self.setHpr(h, hpr[1], hpr[2])

    def setP(self, p):
        hpr = self.getHpr()
        self.setHpr(hpr[0], p, hpr[2])

    def setR(self, r):
        hpr = self.getHpr()
        self.setHpr(hpr[0], hpr[1], r)

    def setPos(self, x, y, z):
        m = list(self._mat)
        m[12:15] = x, y, z
        self._mat = tuple(m)

    def getMat(self):
        return self._mat


def axissystem_to_mat4(a):
    return Mat4(a.x.x, a.x.y, a.x.z, 0,
                a.y.x, a.y.y, a.y.z, 0,
                a.z.x, a.z.y, a.z.z, 0,
                a.origin.x, a.origin.y, a.origin.z, 1
    )


def _blender_to_nodepath(x, y, z, p):
    # TODO: test if it is fine with row-major, column-major, etc.
    mm = (
        x[0], y[0], z[0], 0,
        x[1], y[1], z[1], 0,
        x[2], y[2], z[2], 0,
        p[0], p[1], p[2], 1
    )
    try:
        import Mat4

        ret = NodePath("")
        ret.setMat(Mat4(*mm))
        return ret
    except ImportError:
        ret = dummynodepath(mm)
        return ret


def blender_to_nodepath(mat):
    # TODO: test if it is fine with row-major, column-major, etc.
    m = mat.localOrientation
    p = mat.localPosition
    x = m[0]
    y = m[1]
    z = m[2]
    return _blender_to_nodepath(x, y, z, p)


try:
    from panda3d.core import NodePath, Mat4

    class nodepath_wraps_nodepath(NodePath):
        _matrixview = None

        def set_matrixview(self, matrix_view):
            self._matrixview = matrix_view

        def commit(self):
            if self._matrixview is not None:
                self._matrixview(self)

    class nodepath_wraps_axissystem(NodePath):
        _matrixview = None

        def set_matrixview(self, matrix_view):
            self._matrixview = matrix_view

        def __init__(self, axis):
            self._axis = axis
            NodePath.__init__(self, PandaNode(""))
            self.setMat(axissystem_to_mat4(axis))

        def commit(self):
            from .matrix_spyder import mat4_to_axissystem

            a = mat4_to_axissystem(self.getMat())
            self._axis.x = a.x
            self._axis.y = a.y
            self._axis.z = a.z
            self._axis.origin = a.origin
            if self._matrixview is not None:
                self._matrixview(self._axis)

except ImportError:
    pass


class nodepath_wraps_blender(object):
    _matrixview = None

    def set_matrixview(self, matrixview):
        self._matrixview = matrixview

    def __init__(self, blender):
        self._blender = blender
        nodepath = blender_to_nodepath(blender)
        self._nodepath = nodepath

    def __getattr__(self, attr):
        return getattr(self._nodepath, attr)

    def set_nodepath(self, nodepath):
        self._nodepath = nodepath

    def commit(self):
        from .matrix_blender import nodepath_to_blender

        mat = self.getMat()
        nodepath_to_blender(mat, self._blender)
        if self._matrixview is not None:
            self._matrixview(self._blender)
