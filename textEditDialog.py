from Qt import QtWidgets, QtGui


class TextEditDialog(QtWidgets.QDialog):
    """
    Custom pop-up dialog for editing text purpose, or getting long text input
    """

    def __init__(self, text='', title=''):
        """
        Initializing the dialog ui elements and connect signals

        :param text: str. pre-displayed text
        :param title: str. dialog title
        """
        super(TextEditDialog, self).__init__()

        self.setWindowTitle(title)
        self.ui_textEdit = QtWidgets.QPlainTextEdit(text)
        self.ui_textEdit.setTabStopWidth(self.ui_textEdit.fontMetrics().width(' ') * 4)
        self.ui_acceptButton = QtWidgets.QPushButton("Confirm")

        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.ui_textEdit, 0, 0)
        layout.addWidget(self.ui_acceptButton, 1, 0)

        self.setLayout(layout)
        self.ui_acceptButton.clicked.connect(self.onClickAccept)

    def onClickAccept(self):
        """
        Trigger accept event when clicking the confirm button
        """
        if self.ui_textEdit.toPlainText():
            self.accept()
        else:
            print('value cannot be empty')

    def getTextEdit(self):
        """
        Get the text from text edit field

        :return: str. text from text edit field
        """
        return self.ui_textEdit.toPlainText()

    def closeEvent(self, event):
        """
        Overwrite the close event as it handles accept by default
        """
        self.close()
