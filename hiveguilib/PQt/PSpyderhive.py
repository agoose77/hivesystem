import weakref
from .anyQt import QtGui, QtCore


class PSpyderhive(object):
    def __init__(self, parent, parentwidget):
        self._parent = weakref.ref(parent)
        pw = parentwidget.wrapwidget()
        self.widget = QtGui.QWidget(pw)
        pw.setMinimumSize(800, 50)
        pw.setTitleBarWidget(QtGui.QWidget())
        self.widget.setMinimumSize(800, 50)  # kludge :(
        xp = QtGui.QSizePolicy.Expanding
        policy = QtGui.QSizePolicy(xp, xp)
        self.widget.setSizePolicy(policy)
        # self.widget.setWidgetResizable(True)
        layout = QtGui.QFormLayout()
        self.l_spyderhive = QtGui.QLabel("Parent class")
        self.w_spyderhive = QtGui.QComboBox()
        layout.addRow(self.l_spyderhive, self.w_spyderhive)
        self.widget.setLayout(layout)
        policy = QtGui.QFormLayout.AllNonFixedFieldsGrow
        layout.setFieldGrowthPolicy(policy)
        self.w_spyderhive.currentIndexChanged.connect(self.update)
        self.widget.show()

    def set_candidates(self, candidates):
        self.candidates = list(candidates)
        self.w_spyderhive.clear()
        self.w_spyderhive.addItems([""] + candidates)

    def set_spyderhive(self, spyderhive):
        if not spyderhive:
            self.w_spyderhive.setCurrentIndex(index + 1)
        else:
            index = self.candidates.index(spyderhive)
            self.w_spyderhive.setCurrentIndex(index + 1)

    def update(self, index):
        self._parent().gui_sets_spyderhive(self.candidates[index - 1])
  
  
