import os
import sys

from Qt import QtWidgets, QtCore, QtGui

from jsonViewer.qjsonnode import QJsonNode
from jsonViewer.qjsonview import QJsonView
from jsonViewer.qjsonmodel import QJsonModel


TEST_DICT = {
    "firstName": "John",
    "lastName": "Smith",
    "age": 25,
    "address": {
        "streetAddress": "21 2nd Street",
        "city": "New York",
        "state": "NY",
        "postalCode": "10021"
    },
    "phoneNumber": [
        {
            "type": "home",
            "number": "212 555-1234"
        },
        {
            "type": "fax",
            "number": "646 555-4567"
        }
    ]
}


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        central_widget = QtWidgets.QWidget()
        layout = QtWidgets.QGridLayout()
        line_edit = QtWidgets.QLineEdit()
        temp_btn = QtWidgets.QPushButton('output')
        self.ui_tree_view = QJsonView()

        layout.addWidget(line_edit, 0, 0)
        layout.addWidget(self.ui_tree_view, 1, 0)
        layout.addWidget(temp_btn, 2, 0)

        self.setCentralWidget(central_widget)
        central_widget.setLayout(layout)

        root = QJsonNode.load(TEST_DICT)
        self._model = QJsonModel(root, self)

        # proxy model
        self._proxyModel = QtCore.QSortFilterProxyModel(self)

        self._proxyModel.setSourceModel(self._model)
        self._proxyModel.setDynamicSortFilter(False)
        self._proxyModel.setSortRole(QJsonModel.sortRole)

        self._proxyModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self._proxyModel.setFilterRole(QJsonModel.filterRole)
        self._proxyModel.setFilterKeyColumn(0)

        self.ui_tree_view.setModel(self._proxyModel)

        line_edit.textChanged.connect(self._proxyModel.setFilterRegExp)
        temp_btn.clicked.connect(self.pprint)

    def pprint(self):
        doc = self.ui_tree_view.asDict(self.ui_tree_view.getSelectedIndices())
        print doc


def show():
    global window

    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    show()
