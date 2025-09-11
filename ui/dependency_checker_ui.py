# ui/dependency_checker_ui.py

from PyQt6 import QtCore, QtGui, QtWidgets

class Ui_DependencyCheckerDialog(object):
    def setupUi(self, DependencyCheckerDialog):
        DependencyCheckerDialog.setObjectName("DependencyCheckerDialog")
        DependencyCheckerDialog.resize(550, 300)
        DependencyCheckerDialog.setWindowTitle("Dependency Checker")

        self.verticalLayout = QtWidgets.QVBoxLayout(DependencyCheckerDialog)
        self.verticalLayout.setObjectName("verticalLayout")

        self.textBrowser = QtWidgets.QTextBrowser(parent=DependencyCheckerDialog)
        self.textBrowser.setOpenExternalLinks(True)
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout.addWidget(self.textBrowser)

        self.buttonBox = QtWidgets.QDialogButtonBox(parent=DependencyCheckerDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.buttonBox.accepted.connect(DependencyCheckerDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(DependencyCheckerDialog)