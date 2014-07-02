class KX_GameObject_HiveProxy(object):

    def __init__(self, ori, pos):
        self.localOrientation = ori
        self.localPosition = pos

    def __getattr__(self, attr):
        raise AttributeError("KX_GameObject_HiveProxy only supports localOrientation, localPosition")


class matrixview_panda_local(object):
    def __init__(self, viewedmatrix):
        self.viewedmatrix = viewedmatrix

    def mat(self):
        from .matrix import matrix
        from panda3d.core import NodePath

        mat = matrix(NodePath(""), "NodePath")
        mat.set_matrixview(self.commit)
        return mat

    def commit(self, viewmat):
        wrapmat = self.viewedmatrix._wrapmatrix
        pos0 = viewmat.getPos()
        pos1 = wrapmat.getPos()
        mat0 = viewmat.getMat()
        mat1 = wrapmat.getMat()

        pos = pos0 + pos1
        mat = mat0 * mat1

        # mat contains rotation and translation, so first set mat, then pos
        wrapmat.setMat(mat)
        wrapmat.setPos(pos)


class matrixview_panda_relative(object):
    def __init__(self, viewedmatrix, relativematrix):
        from panda3d.core import Mat4, Mat3

        self.viewedmatrix = viewedmatrix
        assert relativematrix is not None
        self.relmat = Mat4(relativematrix.get_proxy("NodePath").getMat().getUpper3())
        self.relmatinv = Mat4(self.relmat)
        self.relmatinv.invertInPlace()
        self.relpos = relativematrix.get_proxy("NodePath").getPos()

    def mat(self):
        from .matrix import matrix
        from panda3d.core import NodePath

        wrapmat = self.viewedmatrix._wrapmatrix
        pos0 = wrapmat.getPos()
        mat0 = wrapmat.getMat()
        viewmat = NodePath("")
        viewmat.setMat(mat0 * self.relmatinv)
        dpos = pos0 - self.relpos
        dpos2 = self.relmatinv.xformVec(dpos)
        viewmat.setPos(dpos2)
        mat = matrix(viewmat, "NodePath")
        mat.set_matrixview(self.commit)
        return mat

    def commit(self, viewmat):
        from panda3d.core import NodePath, Mat4

        wrapmat = self.viewedmatrix._wrapmatrix
        oldpos = wrapmat.getPos()

        mat = viewmat.getMat() * self.relmat
        pos0 = viewmat.getPos()
        pos0a = self.relmat.xformVec(pos0)
        pos = pos0a + self.relpos

        # mat contains rotation and translation, so first set mat, then pos
        wrapmat.setMat(mat)
        wrapmat.setPos(pos)

class matrixview_blender_relative(object):

    def __init__(self, viewedmatrix, relativematrix):
        import mathutils
        self.viewedmatrix = viewedmatrix
        assert relativematrix is not None
        r = relativematrix.get_proxy("Blender")
        self.relmat = r.localOrientation
        self.relmatinv    = self.relmat.inverted()
        self.relpos = r.localPosition

    def mat(self):
        from .matrix import matrix
        import mathutils
        wrapmat = self.viewedmatrix._wrapmatrix
        pos0 = wrapmat.localPosition
        mat0 = wrapmat.localOrientation
        vmat = mat0 * self.relmatinv
        dpos = pos0 - self.relpos
        dpos2 = self.relmatinv * dpos
        viewmat = KX_GameObject_HiveProxy(vmat, dpos2)
        mat = matrix(viewmat, "Blender")
        mat.set_matrixview(self.commit)
        return mat

    def commit(self, viewmat):
        import mathutils
        wrapmat = self.viewedmatrix._wrapmatrix
        oldpos = wrapmat.localPosition

        mat = viewmat.localOrientation * self.relmat
        pos0 = viewmat.localPosition
        pos0a = self.relmat * pos0
        pos = pos0a + self.relpos

        #mat contains rotation and translation, so first set mat, then pos
        wrapmat.localOrientation = mat
        wrapmat.localPosition = pos

def matrixview_panda(viewedmatrix, mode, secondmatrix=None):
    if mode == "local":
        return matrixview_panda_local(viewedmatrix)
    if mode == "relative":
        return matrixview_panda_relative(viewedmatrix, secondmatrix)
    raise ValueError(mode) #TODO: many

def matrixview_blender(viewedmatrix, mode, secondmatrix=None):
    if mode == "relative":
        return matrixview_blender_relative(viewedmatrix, secondmatrix)
    raise ValueError(mode) #TODO: many

def matrixview(viewedmatrix, mode, secondmatrix=None):
    if viewedmatrix._format == "NodePath":
        return matrixview_panda(viewedmatrix, mode, secondmatrix).mat()
    if viewedmatrix._format == "Blender":
        return matrixview_blender(viewedmatrix, mode, secondmatrix).mat()
    raise ValueError(viewedmatrix._format) #TODO: spyder
