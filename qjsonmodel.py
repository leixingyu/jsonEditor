from Qt import QtWidgets, QtCore, QtGui

from .qjsonnode import QJsonNode


class QJsonModel(QtCore.QAbstractItemModel):
    sortRole = QtCore.Qt.UserRole
    filterRole = QtCore.Qt.UserRole + 1

    def __init__(self, root, parent=None):
        super(QJsonModel, self).__init__(parent)
        self._rootNode = root

    def rowCount(self, parent=QtCore.QModelIndex()):
        if not parent.isValid():
            parentNode = self._rootNode
        else:
            parentNode = parent.internalPointer()

        return parentNode.childCount

    def columnCount(self, parent=QtCore.QModelIndex()):
        return 2

    def data(self, index, role):
        # if not index.isValid():
        #     return None
        # node = index.internalPointer()

        node = self.getNode(index)

        if role == QtCore.Qt.DisplayRole:
            if index.column() == 0:
                return node.key
            elif index.column() == 1:
                return node.value

        elif role == QtCore.Qt.EditRole:
            if index.column() == 0:
                return node.key
            elif index.column() == 1:
                return node.value

        elif role == QJsonModel.sortRole:
            return node.key

        elif role == QJsonModel.filterRole:
            return node.key

    def setData(self, index, value, role):
        # if not index.isValid():
        #     return False
        #
        # node = index.internalPointer()

        node = self.getNode(index)

        if role == QtCore.Qt.EditRole:
            if index.column() == 0:
                node.key = str(value)
                self.dataChanged.emit(index, index)
                return True

            if index.column() == 1:
                node.value = str(value)
                self.dataChanged.emit(index, index)
                return True

        return False

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if section == 0:
                return "Key"
            elif section == 1:
                return "Value"

    def flags(self, index):
        flags = super(QJsonModel, self).flags(index)
        return (QtCore.Qt.ItemIsEditable
                | QtCore.Qt.ItemIsDragEnabled
                | QtCore.Qt.ItemIsDropEnabled
                | flags)

    def index(self, row, column, parent=QtCore.QModelIndex()):
        # if not self.hasIndex(row, column, parent):
        #     return QtCore.QModelIndex()

        parentNode = self.getNode(parent)
        currentNode = parentNode.child(row)
        if currentNode:
            return self.createIndex(row, column, currentNode)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        currentNode = self.getNode(index)
        parentNode = currentNode.parent

        if parentNode == self._rootNode:
            return QtCore.QModelIndex()

        return self.createIndex(parentNode.row(), 0, parentNode)

    def addChildren(self, children, parent=QtCore.QModelIndex()):
        self.beginInsertRows(parent, 0, len(children) - 1)

        if parent == QtCore.QModelIndex():
            parentNode = self._rootNode
        else:
            parentNode = parent.internalPointer()

        for child in children:
            parentNode.addChild(child)

        self.endInsertRows()
        return True

    def removeChild(self, position, parent=QtCore.QModelIndex()):
        self.beginRemoveRows(parent, position, position)

        if parent == QtCore.QModelIndex():
            parentNode = self._rootNode
        else:
            parentNode = parent.internalPointer()

        parentNode.removeChild(position)

        self.endRemoveRows()
        return True

    def clear(self):
        self.beginResetModel()
        self._rootNode = QJsonNode()
        self.endResetModel()
        return True

    def getNode(self, index):
        """
        Custom method
        """
        if index.isValid():
            currentNode = index.internalPointer()
            if currentNode:
                return currentNode
        return self._rootNode

    def asJson(self, index=QtCore.QModelIndex()):
        node = self.getNode(index)
        if node == self._rootNode:
            return node.asJson().values()[0]

        return node.asJson()

        # if index == QtCore.QModelIndex():
        #     node = self._rootNode
        #     return node.asJson().values()[0]
        # else:
        #     node = index.internalPointer()
        #     return node.asJson()
