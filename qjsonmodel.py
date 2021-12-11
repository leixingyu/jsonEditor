"""
The model class used for populating the QJsonView,
and providing functionalities to manipulate QJsonNode objects within the model
"""


from Qt import QtWidgets, QtCore, QtGui

from .qjsonnode import QJsonNode


class QJsonModel(QtCore.QAbstractItemModel):
    sortRole = QtCore.Qt.UserRole
    filterRole = QtCore.Qt.UserRole + 1

    def __init__(self, root, parent=None):
        """
        Initialization

        :param root: QJsonNode. root node of the model, it is hidden
        """
        super(QJsonModel, self).__init__(parent)
        self._rootNode = root

    def rowCount(self, parent=QtCore.QModelIndex()):
        """
        Override
        """
        if not parent.isValid():
            parentNode = self._rootNode
        else:
            parentNode = parent.internalPointer()

        return parentNode.childCount

    def columnCount(self, parent=QtCore.QModelIndex()):
        """
        Override
        """
        return 2

    def data(self, index, role):
        """
        Override
        """
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

        elif role == QtCore.Qt.SizeHintRole:
            return QtCore.QSize(-1, 22)

    def setData(self, index, value, role):
        """
        Override
        """
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
        """
        Override
        """
        if role == QtCore.Qt.DisplayRole:
            if section == 0:
                return "Key"
            elif section == 1:
                return "Value"

    def flags(self, index):
        """
        Override
        """
        flags = super(QJsonModel, self).flags(index)
        return (QtCore.Qt.ItemIsEditable
                | QtCore.Qt.ItemIsDragEnabled
                | QtCore.Qt.ItemIsDropEnabled
                | flags)

    def index(self, row, column, parent=QtCore.QModelIndex()):
        """
        Override
        """
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        parentNode = self.getNode(parent)
        currentNode = parentNode.child(row)
        if currentNode:
            return self.createIndex(row, column, currentNode)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        """
        Override
        """
        currentNode = self.getNode(index)
        parentNode = currentNode.parent

        if parentNode == self._rootNode:
            return QtCore.QModelIndex()

        return self.createIndex(parentNode.row(), 0, parentNode)

    def addChildren(self, children, parent=QtCore.QModelIndex()):
        """
        Custom: add children QJsonNode to the specified index
        """
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
        """
        Custom: remove child of position for the specified index
        """
        self.beginRemoveRows(parent, position, position)

        if parent == QtCore.QModelIndex():
            parentNode = self._rootNode
        else:
            parentNode = parent.internalPointer()

        parentNode.removeChild(position)

        self.endRemoveRows()
        return True

    def clear(self):
        """
        Custom: clear the model data
        """
        self.beginResetModel()
        self._rootNode = QJsonNode()
        self.endResetModel()
        return True

    def getNode(self, index):
        """
        Custom: get QJsonNode from model index

        :param index: QModelIndex. specified index
        """
        if index.isValid():
            currentNode = index.internalPointer()
            if currentNode:
                return currentNode
        return self._rootNode

    def asDict(self, index=QtCore.QModelIndex()):
        """
        Custom: serialize specified index to dictionary
        if no index is specified, the whole model will be serialized
        but will not include the root key (as it's supposed to be hidden)

        :param index: QModelIndex. specified index
        :return: dict. output dictionary
        """
        node = self.getNode(index)
        if node == self._rootNode:
            return node.asDict().values()[0]

        return node.asDict()
