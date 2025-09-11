from PyQt6 import QtCore, QtWidgets

class Ui_PreferencesDialog(object):
    def setupUi(self, PreferencesDialog):
        PreferencesDialog.setObjectName("PreferencesDialog")
        PreferencesDialog.resize(450, 220) # Made taller for the new option
        PreferencesDialog.setWindowTitle("Preferences")
        
        self.verticalLayout = QtWidgets.QVBoxLayout(PreferencesDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        
        # --- Default Output Directory ---
        self.outputDirLayout = QtWidgets.QHBoxLayout()
        self.outputDirLayout.setObjectName("outputDirLayout")
        self.label = QtWidgets.QLabel(parent=PreferencesDialog)
        self.label.setText("Default Output Directory:")
        self.outputDirLayout.addWidget(self.label)
        self.defaultOutputDirLineEdit = QtWidgets.QLineEdit(parent=PreferencesDialog)
        self.defaultOutputDirLineEdit.setObjectName("defaultOutputDirLineEdit")
        self.outputDirLayout.addWidget(self.defaultOutputDirLineEdit)
        self.browseButton = QtWidgets.QPushButton(parent=PreferencesDialog)
        self.browseButton.setText("Browse...")
        self.browseButton.setObjectName("browseButton")
        self.outputDirLayout.addWidget(self.browseButton)
        self.verticalLayout.addLayout(self.outputDirLayout)
        
        # --- Checkboxes ---
        self.clearListCheckBox = QtWidgets.QCheckBox(parent=PreferencesDialog)
        self.clearListCheckBox.setText("Clear file list after all conversions are complete")
        self.clearListCheckBox.setObjectName("clearListCheckBox")
        self.verticalLayout.addWidget(self.clearListCheckBox)
        
        self.saveToSourceCheckBox = QtWidgets.QCheckBox(parent=PreferencesDialog)
        self.saveToSourceCheckBox.setText("Save converted files to their original source directory")
        self.saveToSourceCheckBox.setObjectName("saveToSourceCheckBox")
        self.verticalLayout.addWidget(self.saveToSourceCheckBox)

        # --- NEW: Theme Selection ---
        self.themeLayout = QtWidgets.QHBoxLayout()
        self.themeLabel = QtWidgets.QLabel(parent=PreferencesDialog)
        self.themeLabel.setText("Application Theme:")
        self.themeLayout.addWidget(self.themeLabel)
        
        self.themeComboBox = QtWidgets.QComboBox(parent=PreferencesDialog)
        self.themeComboBox.setObjectName("themeComboBox")
        self.themeLayout.addWidget(self.themeComboBox)
        self.verticalLayout.addLayout(self.themeLayout)
        # --- END NEW ---

        # --- Spacer to push buttons to the bottom ---
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        
        # --- OK and Cancel Buttons ---
        self.buttonBox = QtWidgets.QDialogButtonBox(parent=PreferencesDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        # Connect signals
        self.buttonBox.accepted.connect(PreferencesDialog.accept)
        self.buttonBox.rejected.connect(PreferencesDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(PreferencesDialog)