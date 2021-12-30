"""
Main window to launch JsonViewer
"""


import ast
import json
import os
import sys

from Qt import QtWidgets, QtCore, QtGui
from Qt import _loadUi

from jsonViewer.qjsonnode import QJsonNode
from jsonViewer.qjsonview import QJsonView
from jsonViewer.qjsonmodel import QJsonModel
from jsonViewer.hightlighter import JsonHighlighter


MODULE_PATH = os.path.dirname(os.path.abspath(__file__))
UI_PATH = os.path.join(MODULE_PATH, 'ui', 'jsonEditor.ui')
TEST_DICT = {
    "firstName": "John",
    "lastName": "Smith",
    "age": 35,
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
        _loadUi(UI_PATH, self)

        self.ui_tree_view = QJsonView()
        self.ui_tree_view.setStyleSheet('QWidget{font: 10pt "Bahnschrift";}')
        self.ui_grid_layout.addWidget(self.ui_tree_view, 1, 0)

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

        self.ui_filter_edit.textChanged.connect(self._proxyModel.setFilterRegExp)
        self.ui_out_btn.clicked.connect(self.updateBrowser)
        self.ui_update_btn.clicked.connect(self.updateModel)

        # Json Viewer
        JsonHighlighter(self.ui_view_edit.document())
        self.updateBrowser()

    def updateModel(self):
        text = self.ui_view_edit.toPlainText()
        jsonDict = ast.literal_eval(text)
        root = QJsonNode.load(jsonDict)

        self._model = QJsonModel(root)
        self._proxyModel.setSourceModel(self._model)

    def updateBrowser(self):
        self.ui_view_edit.clear()
        output = self.ui_tree_view.asDict(None)
        jsonDict = json.dumps(output, indent=4, sort_keys=True)
        self.ui_view_edit.setPlainText(str(jsonDict))

    def pprint(self):
        output = self.ui_tree_view.asDict(self.ui_tree_view.getSelectedIndices())
        jsonDict = json.dumps(output, indent=4, sort_keys=True)

        print(jsonDict)


def show():
    global window
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    show()
