import ast

from Qt import QtWidgets, QtCore, QtGui

from .qjsonnode import QJsonNode

# https://doc.qt.io/qt-5/model-view-programming.html#mime-data


class QJsonView(QtWidgets.QTreeView):
    dragStartPosition = None

    def __init__(self):
        super(QJsonView, self).__init__()

        self._clipBroad = ''

        self.setSortingEnabled(1)
        self.setDragEnabled(1)
        self.setAcceptDrops(1)

        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.openContextMenu)

    def setModel(self, model):
        super(QJsonView, self).setModel(model)
        self.model().sort(0, QtCore.Qt.AscendingOrder)

    def openContextMenu(self):
        """
        [summary]

        @param point: QtCore.QPoint
        """

        contextMenu = QtWidgets.QMenu()

        # https://doc.qt.io/qt-5/qitemselectionmodel.html
        proxy_indices = self.selectionModel().selectedRows()
        indices = [self.model().mapToSource(index) for index in proxy_indices]

        # no selection
        if not indices:
            addAction = contextMenu.addAction('add entry')
            addAction.triggered.connect(self.userAdd)

            clearAction = contextMenu.addAction('clear')
            clearAction.triggered.connect(self.clear)

        else:
            copyAction = contextMenu.addAction('copy entry(s)')
            copyAction.triggered.connect(self.copy)

        # single selection
        if len(indices) == 1:
            index = indices[0]

            # only allow add when the index is a dictionary or list
            if index.internalPointer().dtype in [list, dict]:
                addAction = contextMenu.addAction('add entry')
                addAction.triggered.connect(lambda: self.userAdd(index=index))

                if self._clipBroad:
                    pasteAction = contextMenu.addAction('paste entry(s)')
                    pasteAction.triggered.connect(lambda: self.paste(index))


            removeAction = contextMenu.addAction('remove entry')
            removeAction.triggered.connect(lambda: self.remove(index))


        # multiple selction
        elif len(indices) > 1:
            removeMAction = contextMenu.addAction('remove multiple entry')
            removeMAction.triggered.connect(lambda: self.removeChildren(indices))

        cursor = QtGui.QCursor()
        contextMenu.exec_(cursor.pos())

    def serializeSelection(self):
        proxy_indices = self.selectionModel().selectedRows()
        self.indices = [self.model().mapToSource(index) for index in proxy_indices]

        doc = dict()
        if not self.indices:
            doc = self.model().sourceModel().asJson()
        else:
            for index in self.indices:
                doc.update(self.model().sourceModel().asJson(index))

        return doc

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

            mimeData.setData('text/plain', str(self.serializeSelection()))
            drag.setMimeData(mimeData)

            drag.exec_()

    def dragEnterEvent(self, event):
        data = event.mimeData()

        if data.hasFormat('text/plain'):
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        data = event.mimeData()

        if data.hasFormat('text/plain'):
            event.acceptProposedAction()

    def dropEvent(self, event):
        data = event.mimeData()

        if not data.hasFormat('text/plain'):
            return

        index = self.indexAt(event.pos())
        index = self.model().mapToSource(index)

        if not index == QtCore.QModelIndex():
            # Copy
            # self.add(data.text(), index)

            # Move
            for selectedIndex in self.indices:
                self.remove(selectedIndex)

            self.add(data.text(), index)

            event.acceptProposedAction()

    def remove(self, index):
        currentItem = index.internalPointer()
        position = currentItem.row()

        # let the model know we are removing
        self.model().sourceModel().removeChild(position, parent=index.parent())

    def removeChildren(self, indices):
        for index in indices:
            self.remove(index)

    def userAdd(self, dictionary=None, index=QtCore.QModelIndex()):
        from textEditDialog import TextEditDialog

        # test value
        if not dictionary:
            dictionary = {'tes': 'happy', 'apple': { 'migu': 123 }}

        dialog = TextEditDialog(str(dictionary))

        if dialog.exec_():
            text = dialog.getTextEdit()
            self.add(text, index)
            return text
        else:
            return

    def add(self, text=None, index=QtCore.QModelIndex()):
        dictionary = ast.literal_eval(text)

        # populate items with a temp root
        root = QJsonNode.load(dictionary)
        children = root.children

        self.model().sourceModel().addChildren(children, index)
        self.model().sort(0, QtCore.Qt.AscendingOrder)

    def clear(self):
        self.model().sourceModel().clear()

    def copy(self):
        doc = self.serializeSelection()
        self._clipBroad = doc

    def paste(self, index):
        self.userAdd(self._clipBroad, index)
        self._clipBroad = ''
