import ast

from Qt import QtWidgets, QtCore, QtGui

from .qjsonnode import QJsonNode

# https://doc.qt.io/qt-5/model-view-programming.html#mime-data


class QJsonView(QtWidgets.QTreeView):
    dragStartPosition = None

    def __init__(self):
        super(QJsonView, self).__init__()

        self._clipBroad = ''

        self.setSortingEnabled(True)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.openContextMenu)

    def setModel(self, model):
        super(QJsonView, self).setModel(model)
        self.model().sort(0, QtCore.Qt.AscendingOrder)

    def openContextMenu(self):
        contextMenu = QtWidgets.QMenu()

        # https://doc.qt.io/qt-5/qitemselectionmodel.html
        indices = self.getSelectedIndices()

        # no selection
        if not indices:
            addAction = contextMenu.addAction('add entry')
            addAction.triggered.connect(self.customAdd)

            clearAction = contextMenu.addAction('clear')
            clearAction.triggered.connect(self.clear)
        else:
            removeAction = contextMenu.addAction('remove entry(s)')
            removeAction.triggered.connect(lambda: self.remove(indices))

            copyAction = contextMenu.addAction('copy entry(s)')
            copyAction.triggered.connect(self.copy)

        # single selection
        if len(indices) == 1:
            index = indices[0]

            # only allow add when the index is a dictionary or list
            if index.internalPointer().dtype in [list, dict]:
                addAction = contextMenu.addAction('add entry')
                addAction.triggered.connect(lambda: self.customAdd(index=index))

                if self._clipBroad:
                    pasteAction = contextMenu.addAction('paste entry(s)')
                    pasteAction.triggered.connect(lambda: self.paste(index))

        contextMenu.exec_(QtGui.QCursor().pos())

    # helper methods

    def getSelectedIndices(self):
        indices = self.selectionModel().selectedRows()
        return [self.model().mapToSource(index) for index in indices]

    def asDict(self, indices):
        output = dict()
        if not indices:
            output = self.model().sourceModel().asDict()
        else:
            for index in indices:
                output.update(self.model().sourceModel().asDict(index))
        return output

    # overwrite drag and drop

    def mousePressEvent(self, event):
        super(QJsonView, self).mousePressEvent(event)

        if event.button() == QtCore.Qt.LeftButton:
            self.dragStartPosition = event.pos()

    def mouseMoveEvent(self, event):
        # https://stackoverflow.com/questions/10778936/qt-mousemoveevent-qtleftbutton
        # https://doc.qt.io/qt-5/qmouseevent.html#button

        if not event.buttons():
            return

        if not event.buttons() == QtCore.Qt.LeftButton:
            return

        if (event.pos() - self.dragStartPosition).manhattanLength() < QtWidgets.QApplication.startDragDistance():
            return

        if self.selectionModel().selectedRows():
            drag = QtGui.QDrag(self)
            mimeData = QtCore.QMimeData()

            selected = self.asDict(self.getSelectedIndices())
            mimeData.setText(str(selected))
            drag.setMimeData(mimeData)

            drag.exec_()

    def dragEnterEvent(self, event):
        data = event.mimeData()
        if data.hasText():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        data = event.mimeData()
        if data.hasText():
            event.acceptProposedAction()

        dropIndex = self.indexAt(event.pos())
        dropIndex = self.model().mapToSource(dropIndex)

        # not allowing drop to non dictionary or list
        if not dropIndex == QtCore.QModelIndex():
            if dropIndex.internalPointer().dtype not in [list, dict]:
                event.ignore()

    def dropEvent(self, event):
        dropIndex = self.indexAt(event.pos())
        dropIndex = self.model().mapToSource(dropIndex)

        # Move
        data = event.mimeData()
        self.remove(self.getSelectedIndices())
        self.add(data.text(), dropIndex)
        event.acceptProposedAction()

    # custom behavior

    def remove(self, indices):
        for index in indices:
            currentNode = index.internalPointer()
            position = currentNode.row()

            # let the model know we are removing
            self.model().sourceModel().removeChild(position, index.parent())

    def add(self, text=None, index=QtCore.QModelIndex()):
        # populate items with a temp root
        root = QJsonNode.load(ast.literal_eval(text))

        self.model().sourceModel().addChildren(root.children, index)
        self.model().sort(0, QtCore.Qt.AscendingOrder)

    def clear(self):
        self.model().sourceModel().clear()

    def copy(self):
        selected = self.asDict(self.getSelectedIndices())
        self._clipBroad = str(selected)

    def paste(self, index):
        self.customAdd(self._clipBroad, index)
        self._clipBroad = ''
        
    def customAdd(self, text=None, index=QtCore.QModelIndex()):
        from textEditDialog import TextEditDialog

        # test value
        if not text:
            text = "{'tes': 'happy', 'apple': {'migu': 123}}"

        dialog = TextEditDialog(text)
        if dialog.exec_():
            text = dialog.getTextEdit()
            self.add(text, index)
