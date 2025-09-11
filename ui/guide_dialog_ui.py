# ui/guide_dialog_ui.py

from PyQt6 import QtCore, QtGui, QtWidgets

class Ui_SetupGuideDialog(object):
    def setupUi(self, SetupGuideDialog):
        SetupGuideDialog.setObjectName("SetupGuideDialog")
        SetupGuideDialog.resize(600, 450)
        SetupGuideDialog.setWindowTitle("Required Software Setup")

        self.verticalLayout = QtWidgets.QVBoxLayout(SetupGuideDialog)
        self.verticalLayout.setObjectName("verticalLayout")

        self.textBrowser = QtWidgets.QTextBrowser(parent=SetupGuideDialog)
        self.textBrowser.setOpenExternalLinks(True) # Allow opening web links
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout.addWidget(self.textBrowser)

        self.dontRemindCheckBox = QtWidgets.QCheckBox(parent=SetupGuideDialog)
        self.dontRemindCheckBox.setText("Don't show this message on launch")
        self.dontRemindCheckBox.setObjectName("dontRemindCheckBox")
        self.verticalLayout.addWidget(self.dontRemindCheckBox)

        self.buttonBox = QtWidgets.QDialogButtonBox(parent=SetupGuideDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.buttonBox.accepted.connect(SetupGuideDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(SetupGuideDialog)