import weakref
from .anyQt import QtGui, QtCore
from .anyQt.QtGui import QStringListModel, QListView, QCompleter, QValidator
from .anyQt.QtGui import QStyledItemDelegate, QLineEdit, QComboBox


class BlockDelegate(QStyledItemDelegate):
    def __init__(self, completer, validator):
        self._completer = completer
        self._validator = validator
        QStyledItemDelegate.__init__(self)

    def createEditor(self, parent, *args, **kwargs):
        widget = QLineEdit(parent)
        widget.installEventFilter(self)
        widget.setCompleter(self._completer)
        widget.setValidator(self._validator)
        return widget


class BlockValidator(QValidator):
    def __init__(self, model):
        self._model = model
        QValidator.__init__(self)

    def validate(self, inp, pos):
        if len(inp) == 0: return QValidator.Acceptable
        status = QValidator.Invalid
        for s in self._model.stringList():
            if inp == s:
                return QValidator.Acceptable
            elif s.startswith(inp):
                status = QValidator.Intermediate
        return status

    def fixup(self, inp):
        return inp.strip()


class PControllerBlock(object):
    def __init__(self, parent):
        self._parent = weakref.ref(parent)
        self.widget = QtGui.QWidget()
        self.widget.setMinimumWidth(400)  # kludge :(
        xp = QtGui.QSizePolicy.Expanding
        policy = QtGui.QSizePolicy(xp, xp)
        self.widget.setSizePolicy(policy)
        # self.widget.setWidgetResizable(True)
        layout = QtGui.QVBoxLayout()
        self.label = QtGui.QLabel("<i>Block type:</i>")
        layout.addWidget(self.label)
        data = [""] * 10
        self.completer = QCompleter(parent=self.widget)
        self.completer.setModel(QStringListModel())
        self.validator = BlockValidator(self.completer.model())
        model = QStringListModel(data)
        model.dataChanged.connect(self._update)
        view = QListView(self.widget)
        self.delegate = BlockDelegate(self.completer, self.validator)
        view.setItemDelegate(self.delegate)
        view.setAlternatingRowColors(True)
        view.setResizeMode(QListView.ResizeMode(1))
        view.setMovement(QListView.Movement(True))
        #view.setDragDropMode(QListView.InternalMove)
        #view.setDragDropOverwriteMode(False)
        view.setDragDropMode(QListView.NoDragDrop)
        view.setModel(model)
        layout.addWidget(view)
        self.label2 = QtGui.QLabel("Possible values")
        layout.addWidget(self.label2)
        self.combobox = QComboBox()
        self.combobox.setCompleter(self.completer)
        self.combobox.setModel(self.completer.model())
        layout.addWidget(self.combobox)

        self.model, self.view = model, view

        self.widget.setLayout(layout)
        self._added = False

    def set_blocktype(self, blocktype):
        if blocktype is None:
            self.label.setText("<i>Block type:</i>")
        else:
            self.label.setText("<i>Block type:</i>  <b>%s</b>" % blocktype)

    def set_blockvalues(self, blockvalues):
        data = [""] * 10
        if blockvalues is not None:
            for n, s in enumerate(blockvalues[:10]):
                data[n] = s
        self.model.setStringList(data)

    def set_blockstrings(self, blockstrings):
        if blockstrings is None: blockstrings = [""] * 10
        self.blockstrings = blockstrings
        self.completer.model().setStringList(blockstrings)

    def _update(self, *args, **kwargs):
        blockvalues = [str(s) for s in self.model.stringList()]
        for b in blockvalues:
            if b != "" and b not in self.blockstrings: return

        parent = self._parent()
        ok = parent.gui_updates_blockvalues(blockvalues)
        # ignoring "ok" for now: value restore is done by parent

    def show(self):
        if not self._added:
            parent = self._parent()
            pwindow = parent._pwindow()
            subwin = pwindow._subwin
            subwin.setWidget(self.widget)
            self._added = True
        self.widget.show()

    def hide(self):
        self.widget.hide()
